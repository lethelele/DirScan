
import requests
from concurrent.futures import ThreadPoolExecutor
import threading
from tqdm import tqdm
import time
import random
from urllib.parse import urljoin
import signal
import sys
from pyfiglet import figlet_format

# 全局信号标记
global is_interrupted
is_interrupted = False
# ============== 新增全局计数器 ==============
completed_paths = 0  # 已完成路径计数
total_requests = 0  # 总请求数（含重试）
# ==========================================
# 结果统计
results = {
    "found": [],  # 找到的有效路径
    "errors": 0,  # 错误计数
    "blocked": 0  # 被限流计数
}
# 线程安全锁
lock = threading.Lock()


    # 信号处理函数

def signal_handler(signal_num, frame):
    global is_interrupted
    is_interrupted = True
    print("\n\033[91m[!] 检测到用户中断请求，正在停止扫描...\033[0m")

    # 注册Ctrl+C信号监听

signal.signal(signal.SIGINT, signal_handler)



def logo(string, color):
    """
    为字符串填充颜色
    Arguments:
        string {str} -- 用于应用颜色的字符串
        color {int} -- 要应用的颜色值
    """
    return ("\033[%sm%s\033[0m" % (color, string))


print(logo(figlet_format("dirscan", font="small"), 92))



def input_result():
    global target_url, dict_path, threads, paths
    # 用户输入
    target_url = input("输入目标URL: ").strip()
    dict_path = input("请输入字典路径(回车默认): ").strip() or "dict.txt"
    threads_input = input("请输入线程数(回车默认为100):").strip()
    threads = int(threads_input) if threads_input.isdigit() else 100
    # 读取字典文件
    try:
        with open(dict_path, "r", encoding="utf-8") as f:
            paths = list(line.strip() for line in f if line.strip())
    except Exception as e:
        print(f"读取字典失败: {e}")
        sys.exit(1)



def check_path(path,i):
    global  completed_paths, total_requests

    if is_interrupted:
        return

    session = requests.Session()
    full_url = urljoin(target_url + "/", path)


    # 更新总请求数
    with lock:
        total_requests += 1

    for attempt in range(3):
        if is_interrupted:
            return

        try:
            # 随机延迟防止封禁
            if random.random() > 0.7:  # 30%概率添加额外延迟
                time.sleep(random.uniform(0.1, 0.5))

            response = session.get(
                full_url,
                timeout=8,
                allow_redirects=False
            )

            # 处理限流情况
            if response.status_code == 429:
                with lock:
                    results["blocked"] += 1


                # 指数退避等待
                wait_time = min(2 ** attempt, 15)

                # ========= 关键修改：非阻塞等待+进度更新 =========
                start_wait = time.time()
                while (time.time() - start_wait < wait_time) and not is_interrupted:
                    time.sleep(0.1)  # 短间隔检查

                    # 更新进度显示
                    # with lock:
                    #     if progress_bar:
                    #         progress_bar.set_postfix({
                    #             "发现": len(results["found"]),
                    #             "限流": results["blocked"],
                    #             "重试": results["retries"]
                    #         })
                # ============================================

                continue  # 重试请求

            # 找到有效路径
            if response.status_code in [200, 301, 302, 304, 403]:
                with lock:
                    results["found"].append((i, response.status_code, full_url))
                    status_color = {
                        200: "\033[92m",  # 绿色
                        403: "\033[95m",  # 紫色
                        301: "\033[94m",  # 蓝色
                        302: "\033[94m",
                        304: "\033[94m"
                    }
                    color = status_color.get(response.status_code, "")
                    tqdm.write(f"{color}[Found] [{i}] {response.status_code} {full_url}\033[0m")
                break  # 找到路径后退出重试循环

            # 其他状态码不重试
            break

        except requests.RequestException as e:
            with lock:
                #print(e)
                results["errors"] += 1
            break

    # 路径处理完成
    with lock:
        completed_paths += 1
        #print(completed_paths)
        # if progress_bar:
        #     progress_bar.n = completed_paths
        #     progress_bar.refresh()

# 主扫描函数
def run_scan():
    global progress_bar, completed_paths, total_requests

    print("=" * 50)
    print(f"使用字典: {dict_path}")
    print(f"目标URL: {target_url}")
    print("字典乱序: 启用")
    print("随机UA头: 启用")
    print("IP随机化: 启用")
    print(f"线程数: {threads}")
    print("=" * 50)

    # # 重置计数器
    completed_paths = 0
    total_requests = 0

    with ThreadPoolExecutor(max_workers=threads) as executor:
        # 提交所有任务
        shuffled_paths = paths.copy()
        random.shuffle(shuffled_paths)
        futures = [executor.submit(check_path, shuffled_paths[path], path) for path in range(len(shuffled_paths))]
        # 创建进度条
        with tqdm(total=len(paths)) as pbar:
            progress_bar = pbar

            #
            # # ===== 进度监控循环 =====
            while completed_paths < len(paths) and not is_interrupted:
                time.sleep(0.2)  # 更新间隔

                # 更新进度条和统计信息
                pbar.n = completed_paths
                # print(completed_paths)
                pbar.set_postfix({
                    "发现": len(results["found"]),
                    "限流": results["blocked"]
                })
                pbar.refresh()

            # 中断处理
            if is_interrupted:
                print("\n\033[91m[!] 正在取消剩余任务...\033[0m")
                for future in futures:
                    future.cancel()
def start():
    # 启动扫描
    start_time = time.time()
    run_scan()
    end_time = time.time()

    # 输出最终结果
    print("=" * 50)
    print("扫描结束!")
    print(f"总耗时: {end_time - start_time:.2f}秒")
    print(f"发现有效路径: {len(results['found'])}条")
    print(f"错误请求: {results['errors']}次")
    print(f"限流次数: {results['blocked']}次")


    # 保存结果到文件
    if results["found"]:
        with open("scan_results.txt", "w", encoding="utf-8") as f:
            for i, status, url in results["found"]:
                f.write(f"{i} {status} {url}\n")
        print("结果已保存到 scan_results.txt")


















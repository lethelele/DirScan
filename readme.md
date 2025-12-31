# 前言

 **该版本为基础款，若想实现随机UA头、IP伪装、自定义文件后缀扫描功能，请赞赏作者10￥，并qq邮箱留言"我要进阶款"，附上支付截图。我将打包邮箱发给你。**

## 核心功能 

# 环境搭建

工具适用在python3版本

```
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple  
```

# 工具介绍

一款高性能、高隐蔽性的目录扫描工具，专为渗透测试与网站安全检测设计，提供随机UA头、IP伪装、线程并发多维度防封禁机制。 

### 1、智能路径扫描 

支持多类型文件精准筛选：PHP、ASP(X)、JSP、备份文件、自定义后缀  - 内置动态字典加载，支持自定义字典路径导入，自动化识别200、301、302、403等多类有效返回码。

### 2、高隐蔽防封禁  

**随机User-Agent池**：内置20+浏览器UA头随机切换，模拟真实浏览器访问。

**IP伪装**：动态生成公网/内网随机IP头，支持X-Forwarded-For、X-Real-IP等多类型伪造。

**智能延迟**：30%概率随机添加0.1-0.5秒访问延迟，规避高频访问检测。  

**指数退避重试**：遭遇429限流自动执行指数退避等待，最高支持3次重试。

### 3、并发任务优化 

可自定义线程数，默认100线程高速扫描  - 基于ThreadPoolExecutor实现线程池调度，避免资源泄漏  - 线程安全计数器，实时统计扫描进度、错误请求、限流次数。

### 4、实时可视化输出 

 终端进度条动态展示扫描进度，彩色化状态码高亮显示：200绿色、403紫色、3XX跳转蓝色 。支持用户Ctrl+C中断扫描并安全退出，自动取消剩余任务。

在命令行下运行

```
python dirscan.py
```

![image-20251231234537054](C:\Users\Administrator.Lethe\AppData\Roaming\Typora\typora-user-images\image-20251231234537054.png)

![image-20251231234632080](C:\Users\Administrator.Lethe\AppData\Roaming\Typora\typora-user-images\image-20251231234632080.png)

结果将保存在同目录下的scan_results.txt文件中

![image-20251231234909101](C:\Users\Administrator.Lethe\AppData\Roaming\Typora\typora-user-images\image-20251231234909101.png)

# 赞赏作者

如果觉得工具好用，就给点赞赏支持一下吧

支付宝

<img src="C:\Users\Administrator.Lethe\Downloads\1767196414445.jpg" alt="1767196414445" style="zoom: 33%;" />

微信

<img src="C:\Users\Administrator.Lethe\Downloads\mm_facetoface_collect_qrcode_1767196526326.png" alt="mm_facetoface_collect_qrcode_1767196526326" style="zoom:33%;" />

# 联系作者

有问题欢迎联系：3106347004@qq.com
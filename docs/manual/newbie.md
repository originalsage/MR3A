---
order: 1
icon: ri:guide-fill
---
<!-- markdownlint-disable MD033 -->
# 新手上路

## 前置准备

### 1. 确认版本系统

<div align="center">

| | Windows | macOS | Linux |
| :---: | :---: | :---: | :---: |
| 系统要求 | Windows 10 及以上 | 自行尝试 | 自行尝试 |
| 需要配置环境 | 是 | 是 | 是 |
| 需要模拟器 | 是 | 是 | 模拟器或容器化安卓 |

| | 备注 |
| --- | --- |
| Windows 用户 | 绝大部分情况请下载 x86_64 架构 |

</div>

***

### 2. 下载正确的版本

MR3A 下载（更新）地址： [GitHub 发布页](https://github.com/originalsage/MR3A/releases)  。点击链接后，在 `Assets` 处选择适配您系统的最新版压缩包下载。

- **Windows**：`MR3A-win-x86_64-vXXX.zip`
- **macOS**：`MR3A-macos-x86_64-vXXX.tar.gz` 或 `MR3A-macos-aarch64-vXXX.tar.gz`（取决于架构）
- **Linux**：`MR3A-linux-x86_64-vXXX.tar.gz` 或 `MR3A-linux-aarch64-vXXX.tar.gz`（取决于架构）

<details>
  <summary>Mac用户查看处理器架构方法</summary>
  <p></p>
  <blockquote>
    <ol>
      <li>点击屏幕左上角的苹果标志。</li>
      <li>选择"关于本机"。</li>
      <li>在弹出的窗口中，你可以看到处理器的信息。</li>
    </ol>
    <ul>
      <li>若使用 Intel X86 处理器，请下载 <code>MR3A-macos-x86_64-vXXX.tar.gz</code></li>
      <li>若使用 Apple Silicon 系列如：M1、M2 等 ARM 架构处理器，请下载 <code>MR3A-macos-aarch64-vXXX.tar.gz</code></li>
    </ul>
  </blockquote>
</details>

***

### 3. 下载适合的模拟器

- **Windows**：推荐 MuMu、雷电等主流模拟器，详见 [Windows 模拟器支持](https://docs.maa.plus/zh-cn/manual/device/windows.html)
- **macOS**：可参考 [macOS 模拟器文档](https://docs.maa.plus/zh-cn/manual/device/macos.html)
- **Linux**：可参考 [Linux 模拟器文档](https://docs.maa.plus/zh-cn/manual/device/linux.html)

***

### 4. 正确设置分辨率

模拟器默认分辨率即可（`16:9` 横屏），推荐 `1920x1080` 或 `1280x720`。

MR3A 运行前会自动检查，不符合时会提示。

### 5. 启动 MR3A

MR3A 使用前请确保已正确解压压缩包。

::: warning 注意
不要在压缩软件直接打开程序！
:::

#### Windows

确认解压完整，并确保将 MR3A 解压到一个独立的文件夹中。推荐解压路径如：`D:\MR3A`。除关闭内建管理员批准的Administrator账号外，请勿将 MR3A 解压到如 `C:\`、`C:\Program Files\` 等需要 UAC 权限的路径。

- 解压后运行 `MR3A.exe` 即可。若运行失败，先运行 `DependencySetup_依赖库安装.bat` 安装依赖，仍失败则查看 [附录](#appendix) 手动排查。

#### macOS

<details>
  <summary>详情</summary>
  <p></p>
  <blockquote>

1. 打开终端，解压分发的压缩包：

    **选项1：解压到系统目录（需要管理员权限）**

    ```shell
    sudo mkdir -p /usr/local/bin/MR3A
    sudo tar -xzf <下载的MR3A压缩包路径> -C /usr/local/bin/MR3A
    ```

    **选项2：解压到用户目录（推荐，无需sudo）**

    ```shell
    mkdir -p ~/MR3A
    tar -xzf <下载的MR3A压缩包路径> -C ~/MR3A
    ```

2. 进入解压目录并运行程序：

    ```shell
    cd /usr/local/bin/MR3A
    ./MR3A
    ```

若想使用**图形操作页面**请按第二步操作，执行 `MR3A` 程序即可。

⚠️Gatekeeper 安全提示处理：

在 macOS 10.15 (Catalina) 及更高版本中，Gatekeeper 可能会阻止运行未签名的应用程序。  
如果遇到"无法打开，因为无法验证开发者"等错误，请选择以下任一方案:

```shell
# 方案1：以 MR3A 为例，移除隔离属性（推荐，以实际路径为准）
sudo xattr -rd com.apple.quarantine /usr/local/bin/MR3A/MR3A
# 或用户目录版本：xattr -rd com.apple.quarantine ~/MR3A/MR3A

# 方案2：添加到 Gatekeeper 白名单
sudo spctl --add /usr/local/bin/MR3A/MR3A
# 或用户目录版本：spctl --add ~/MR3A/MR3A

# 方案3：一次性处理整个目录
sudo xattr -rd com.apple.quarantine /usr/local/bin/MR3A/*
# 或用户目录版本：xattr -rd com.apple.quarantine ~/MR3A/*
```

  </blockquote>
</details>

#### Linux

同 macOS，下载对应版本的压缩包，解压后运行 `MR3A` 即可。

### 6. 开始使用

建议先跟随软件内置教程快速了解各个功能。

教程位置：MR3A软件左下角「设置」→「关于我们」→ 页面底部「使用教程」

观看完内置教程后，参照下图操作：

1. 点击右上角「刷新」和「重新连接」，确认模拟器已连接。若未自动连接或连接失败，请先确认模拟器已启动，再阅读 [连接设置](./connection.md) 手动排查。
2. 勾选需要运行的任务，点击「开始任务」即可。

![MR3A 连接与任务界面](/images/newbie-main-interface-connection.webp)

任务开始运行后。当出现类似如下「任务完成」提示时，就说明一切正常：

![MR3A 任务完成](/images/newbie-task-complete.webp)

恭喜，你已经成功上手 MR3A！

### 7. 了解更多

成功运行一次脚本后，建议按需查看以下文档：

- [配置说明](./config.md) — 了解软件设置中的选项和按钮功能
- [使用场景](./scenarios.md) — 多开、定时等使用场景的操作指南
- [常见问题](./faq.md) — 遇到问题时先来这里找答案

### 附录：手动安装运行环境 {#appendix}

::: tip 提示
绝大多数用户无需手动安装本节内容。如果 MR3A 启动失败，运行解压目录下的 `DependencySetup_依赖库安装.bat` 即可自动安装。该 bat 也失败时再来看这节。
:::

<div align="center">

<table>
  <thead>
    <tr>
        <th><div align="center">启动方式</div></th>
        <th><div align="center">Windows</div></th>
        <th><div align="center">macOS</div></th>
        <th><div align="center">Linux</div></th>
    </tr>
  </thead>
  <tbody>
    <tr>
        <td><div align="center">需安装<br>VCRedist</div></td>
        <td><div align="center">点击 <a href="https://aka.ms/vs/17/release/vc_redist.x64.exe" target="_blank">vc_redist.x64</a> 下载或通过 winget 安装（详见下方）</div></td>
        <td colspan="2"><div align="center">否</div></td>
    </tr>
    <tr>
        <td><div align="center">需安装<br>.NET 10</div></td>
        <td><div align="center">前往 <a href="https://dotnet.microsoft.com/zh-cn/download/dotnet/10.0" target="_blank">.NET 官方下载页面</a> 下载对应版本或<br>通过 winget 安装（详见下方）</div></td>
        <td><div align="center"><a href="https://dotnet.microsoft.com/zh-cn/download/dotnet/10.0" target="_blank">.NET 官方下载页面</a></div></td>
        <td><div align="center">同 Mac</div></td>
    </tr>
    <tr>
       <td><div align="center">需安装<br>Python</div></td>
        <td colspan="2"><div align="center">压缩包自带，无需其他操作</div></td>
        <td><div align="center">需要 Python 3.10 ≤ version < 3.14</div></td>
    </tr>
  </tbody>
</table>

</div>

#### 1. VCRedist x64

Windows 用户**必须安装 VCRedist x64**：这是运行 MR3A 的基础需求。

<details>
  <summary>详细安装方式</summary>
  <p></p>
  <blockquote>
    <ul>
      <li>
        直接下载：点击
        <a href="https://aka.ms/vs/17/release/vc_redist.x64.exe" target="_blank">vc_redist.x64</a>
        下载并安装
      </li>
      <li>
        <code>winget</code> 安装：右键 Windows 开始按钮，选择"命令提示符"或"PowerShell (管理员)"，然后在终端内粘贴以下命令并回车：
        <pre><code>winget install Microsoft.VCRedist.2017.x64</code></pre>
      </li>
    </ul>
  </blockquote>
</details>

#### 2. .NET 10

所有用户都需要自行下载并安装适用于您系统的 .NET 10 。

<details>
  <summary>详细安装方式</summary>
  <p></p>
  <blockquote>
    <ul>
      <li>
        自行下载：点击
        <a href="https://dotnet.microsoft.com/download/dotnet/10.0" target="_blank">.NET 官方下载页面</a>
        ，选择适合您系统的版本下载并安装。
        <div align="center">
          <table>
            <thead>
              <tr>
                <th></th>
                <th>Windows</th>
                <th>macOS</th>
                <th>Linux</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>您需要下载</td>
                <td colspan="1">.NET 桌面运行时</td>
                <td colspan="2">.NET 运行时</td>
              </tr>
              <tr>
                <td>安装程序</td>
                <td>x64</td>
                <td colspan="2">
                  <a href="https://builds.dotnet.microsoft.com/dotnet/scripts/v1/dotnet-install.sh" target="_blank">dotnet-install.sh</a>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </li>
      <li>
        （仅 Windows 用户）<code>winget</code> 安装：右键 Windows 开始按钮，选择"命令提示符"或"PowerShell (管理员)"，然后在终端内粘贴以下命令并回车：
        <pre><code>winget install Microsoft.DotNet.DesktopRuntime.10</code></pre>
      </li>
    </ul>
  </blockquote>
</details>

#### 3. Python

Linux 用户需要单独安装 Python，Windows和macOS压缩包自带，无需其他操作。

<details>

<summary>详情</summary>

<p></p>

<blockquote>

- 您的系统需要安装 **Python 版本 ≥ 3.10**。这是 MR3A 启动和管理其内部环境所必需的。
- MR3A 首次运行时会自动创建并使用独立的虚拟环境，并安装所需的 Python 依赖包 (来自 `requirements.txt`)。您**无需**手动创建虚拟环境或安装这些依赖。

</blockquote>

 </details>

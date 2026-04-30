# Wenfxl Codex Manager Web 控制台
[![Telegram Group](https://img.shields.io/badge/Telegram-Community_Chat-0088cc?style=for-the-badge&logo=telegram)](https://t.me/+4AmjbVPvvRgxMDVl)
[![License](https://img.shields.io/badge/License-CC_BY--NC_4.0-lightgrey?style=for-the-badge)](https://creativecommons.org/licenses/by-nc/4.0/legalcode)

一个面向高并发账号注册与全生命周期库存管理的高级分布式自动化平台。它作为集中式 Web 编排中枢，可以将分布式浏览器扩展工作节点（Classic 模式）、多后端邮箱引擎，以及企业级云仓库（CPA/Sub2API）无缝同步到统一的主从生态中。

它集成了：
- 多后端邮箱 OTP 获取
- 注册任务编排
- 代理 / Clash / Mihomo 切换
- CPA 仓库维护
- Sub2API 仓库维护
- AI 驱动的资料与子域名生成（Codex）
- 本地账号库存、导出、删除与实时日志流

它也支持 **随机多级子域名生成**，适合与下列自定义邮箱后端配合使用：
- <https://github.com/wenfxl/freemail>
- <https://github.com/wenfxl/cloud-mail>
- <https://github.com/wenfxl/cloudflare_temp_email_worker>

> 仅可在你拥有或已明确获授权测试的系统和环境中使用。
> 请确保你的使用方式符合适用法律、平台规则和服务条款。

## 🚀 支持环境
* **Windows**：原生支持（推荐 **Python 3.12.6 或 Python 3.12**）。
* **Linux**：原生支持（**AMD64** 与 **ARM64**）。
* **macOS**：原生支持（**Apple Silicon M1/M2/M3/M4/intel**）。
* **Docker**：**全平台支持（强烈推荐）**。
* 提供多架构镜像，可在各类云环境和本地环境中无缝部署。

## ⚠ 重要运行说明
* **原生 macOS / Linux**：原生运行时 **必须** 使用 **Python 3.11**，以确保与核心引擎兼容。
* **原生 Windows**：请使用 **Python 3.12.6 或 Python 3.12**，以匹配核心引擎要求。
* **Docker 部署**：这是 **推荐方式**。镜像已预配置优化后的运行环境，可以真正开箱即用，无需担心 Python 版本问题。

## 环境准备

安装 Python 依赖。使用根目录中的 `requirements.txt` 安装所需基础库：

```bash
pip install -r requirements.txt
```

## ☕ 请我喝杯咖啡

如果你觉得这个工具有帮助，或它帮你节省了时间，可以考虑请我喝杯咖啡。你的支持是持续维护和更新的重要动力。
- ⚡ **Afdian:** [https://ifdian.net/a/wenfxl](https://ifdian.net/a/wenfxl)
- 🪙 **USDT (TRX/Tron/TRC20):** `TLMNmyfUajfGSBhUfJ1orqxpvv7BWFnDqN`

## Web 控制台预览

<details>
<summary><strong>点击展开 Web 控制台截图</strong></summary>

### 1. 登录界面

![Login Screen](./assets/manager1.png)

### 2. 主仪表盘

![Main Dashboard](./assets/manager2.png)

### 3. 集群控制

![Cluster Control](./assets/manager3.png)

### 4. 邮箱配置 / 多级子域名设置

![Mailbox Configuration / Multi-level Subdomain Settings](./assets/manager4.png)

### 5. Microsoft 邮箱库

![Microsoft Mail Lib](./assets/manager5.png)

### 6. 账号库存

![Account Inventory](./assets/manager6.png)

### 7. 云端库存

![Cloud Inventory](./assets/manager7.png)

### 8. 短信验证

![SMS Verification](./assets/manager8.png)

### 9. 网络代理设置

![Network Proxy Settings](./assets/manager9.png)

### 10. 中转仓库

![Transit Warehouse](./assets/manager10.png)

### 11. 通知

![Notifications](./assets/manager11.png)

### 12. 并发与系统设置

![Concurrency and System Settings](./assets/manager12.png)

</details>

## 功能特性

### Web 控制台与运行时控制
- **Web 可视化控制台**：当前版本主要通过浏览器控制面板进行管理，而不是仅依赖配置文件工作流。
- **无缝配置升级**：后端会自动检测缺失的配置键，并从 `config.example.yaml` 合并默认值，确保系统更新期间不会停机或白屏。
- **分布式集群控制**：支持真正的多节点架构。跨多台机器部署时，任意节点都可作为主控中心。你可以通过单个 **Cluster Control** 面板远程编排启动/停止命令、查看跨机器日志流，并从整个集群提取账号。
- **密码登录 + Bearer 会话**：控制台使用密码登录，并通过基于 token 的认证 API 执行操作。
- **实时日志流**：后端日志通过 SSE 推送到页面，便于实时监控。
- **任务编排**：支持一键启动 / 停止，并可自动识别 `normal`、`CPA` 或 `Sub2API` 模式。
- **实时统计仪表盘**：实时显示成功、失败、重试、耗时、进度和当前模式。
- **多渠道通知**：支持通过 Webhook 或 Telegram 机器人发送实时任务完成报告、库存告警和系统异常，配置入口位于 **Notifications** 面板。

### 分布式浏览器扩展模式（“Classic” 插件架构）
- **集中主控，分散工作节点**：核心管理器只需部署一次。在多个浏览器中安装自定义浏览器扩展后（甚至可跨不同物理机器），它们会自动连接回主控控制台。
- **真实浏览器指纹**：避免无头自动化框架（如 Playwright 或 Puppeteer）经常触发的严格机器人检测。任务会在真实浏览器环境中执行。
- **即插即用的工作节点**：任何安装了扩展的浏览器都会立即成为分布式工作节点。Web 控制台负责任务分发、收集执行日志，并集中提取生成的账号。

### AI 资料与子域名增强（Codex）
  - **真实资料生成**：自动调用 AI 模型（例如 `gpt-5.1-codex`）生成用于注册的欧美风格真实姓名（`firstname.lastname`）。
  - **智能技术子域名**：生成热门技术 / AI 关键词（例如 `vector-database`、`neural`），并无缝注入多级子域名生成器，显著提升账号可信度。

### 邮箱与 OTP 工作流
- **多后端邮箱支持**：支持 `cloudflare_temp_email`、`freemail`、`imap`、`cloudmail`、`mail_curl`、`luckmail`、`TempMail.org`、`Tempmail.lol`、`Duckmail`、`Generator`、`hotmail/outlook` 和 `GmailOauth`。
- **多域名轮换**：支持以逗号分隔多个邮箱域名，并在生成地址时随机选择。
- **随机多级子域名生成**：可以批量生成随机子域名，包括多级子域名结构。
- **子域名池接管**：启用子域名模式后，生成的子域名可直接替换常规邮箱域名池，用于后续注册任务。
- **兼容后端的子域名工作流**：多级子域名生成设计用于配合 `freemail`、`cloud-mail` 和 `cloudflare_temp_email_worker` 等自定义邮箱后端 / 泛域名后端。
- **HeroSMS 集成**：完整支持短信验证，包括实时余额检查、全球价格 / 库存面板，以及自动选择国家以避开黑名单和超时。
- **LuckMail 高级控制**：内置支持通过 API 直接购买邮箱、自动标记购买记录、使用“历史复用”模式节省成本，以及手动批量购买控制台。
- **Microsoft 资产隔离**：专用 **Microsoft Mail Lib** 模块可单独存储、分类和管理 Microsoft 账号，使其与标准本地库存分离。

### 代理管理与网络韧性
- **Clash / Mihomo 节点轮换**：可在注册任务前通过 Clash API 切换出站节点。
- **最快节点优先模式**：支持 `fastest_mode: true`，可基于延迟优先选择节点。
- **多线程 Clash 代理池模式**：支持通过 `clash_proxy_pool.pool_mode` + `warp_proxy_list` 组合使用多容器 / 多端口代理池。
- **Docker 感知代理适配**：在容器内需要时，会自动将 `127.0.0.1` / `localhost` 重写为 `host.docker.internal`。
- **区域感知可用性检查**：验证出站连通性，并拒绝被阻断或不适合的区域，例如 `CN` / `HK`。
- **重试处理**：对不稳定网络、OTP 轮询和临时请求失败包含重试与冷却逻辑。

### 库存维护与仓库操作
- **云端库存监控**：通过 **Cloud Inventory** 仪表盘实时跟踪远程 API 余额、库存水平和账号状态。
- **独立可用性检查**：Web 控制台中的专用“Manual Check”按钮只会扫描并清理 CPA/Sub2API 仓库中的失效账号，不会触发主注册循环。
- **快速补货开关**：`auto_check` 开关可在补货前跳过完整库存检查，仅基于云 API 总数量快速推进循环。
- **本地 SQLite 库存**：本地存储账号，并在面板中提供分页库存浏览。
- **批量导出 / 删除**：支持将选中账号导出为 JSON 或 TXT，也支持批量删除选中账号。
- **可选 CPA 维护模式**：可定期检查 CPA 库存，并在有效账号数量较低时自动补货。
- **多线程 CPA 检查**：CPA 健康检查并发处理，工作线程数量由 `cpa_mode.threads` 控制。
- **CPA 上传集成**：可以将新生成的凭据直接上传到 CPA，并从面板触发推送动作。
- **Sub2API 仓库模式**：支持对 Sub2API 执行周期检查、补货、推送同步和 token 刷新处理。
- **Sub2API 直接推送**：可直接从 Web 控制台将选中账号推送到 Sub2API。
- **配额阈值处理**：支持基于剩余周配额百分比阈值的可配置周配额逻辑。
- **禁用或删除行为控制**：你可以通过配置决定耗尽或永久失效的账号是仅禁用，还是物理删除。
- **凭据刷新救援**：当已存储凭据失效时，脚本可尝试通过 refresh token 恢复，并更新 CPA / Sub2API 存储。

### 归档输出与隐私保护
- **本地 SQLite 数据库**：生成的 token 和账号凭据现在会安全地存入集中式本地数据库，而不是分散的 JSON 文件，从而保持文件系统更整洁。
- **CPA / Sub2API 模式下的可选本地保留**：启用后，即使账号已成功推送到云仓库，上传工作流仍可保留一份本地数据库副本。
- **控制台导出支持**：数据库中存储的账号可直接从 Web 控制台选中并导出为结构化 JSON 或 `email----password` TXT 文件。
- **日志脱敏**：支持在控制台输出中隐藏邮箱域名，以保护敏感域名配置。

## 项目结构

本仓库核心目录和文件概览：

```text
.
├── wfxl_openai_regst.py     # 主 Web 控制台入口
├── global_state.py          # 全局状态管理（token、节点与集群锁）
├── routers/                 # API 路由端点
├── utils/                   # 核心引擎与配置管理
│   ├── email_providers/     # 邮箱后端实现
│   └── integrations/        # 第三方 API 集成（Sub2API、TG Bot、HeroSMS）
├── luckmail/                # 高级 LuckMail 服务集成
├── static/                  # Web 控制台前端资源（Vue.js、CSS）
├── assets/                  # README 截图资源
├── public/                  # 分布式浏览器扩展文件（“Classic” 模式）
├── data/                    # 运行时数据、SQLite DB、本地配置与导出
├── index.html               # 前端 UI 入口
├── Dockerfile               # 容器镜像定义
├── docker-compose.yml       # Docker compose 部署示例
├── config.example.yaml      # 配置回退模板
├── requirements.txt         # Python 依赖列表
└── README.md                # 项目文档
```

## 使用方式

在本地启动 Web 控制台服务：

```bash
python wfxl_openai_regst.py
```

启动后，在浏览器中打开 Web 控制台：

```text
http://127.0.0.1:8000
```

默认 Web 控制台密码：

```text
admin
```

推荐工作流：
仓库包含一个开箱即用的 `docker-compose.yml`，可用于启动带持久化配置和数据挂载的 **Wenfxl Codex Manager Web Console**。
- 登录 Web 控制台
- 在 UI 中配置邮箱 / 代理 / 仓库设置
- 从仪表盘启动或停止任务
- 实时监控日志、任务状态和账号库存

## 使用 Docker Compose 运行

仓库包含一个开箱即用的 `docker-compose.yml`，可用于启动带持久化配置和数据挂载的 **Wenfxl Codex Manager Web Console**。

当前 compose 示例：

```yaml
version: '3.8'

services:
  codex-web:
    image: wenfxl/wenfxl-codex-manager:latest
    container_name: wenfxl_codex_manager
    ports:
      - "8000:8000"
    restart: always
    extra_hosts:
      - "host.docker.internal:host-gateway"
    environment:
      - HOST_PROJECT_PATH=${PWD}
    volumes:
      - ./data:/app/data
      - /var/run/docker.sock:/var/run/docker.sock
  watchtower:
    image: containrrr/watchtower
    container_name: watchtower
    restart: always
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    command: --interval 86400 --cleanup

```

仓库也包含一个开箱即用的 `docker-compose2.yml`，可用于启动带持久化配置和数据挂载的 **Wenfxl Codex Manager Web Console**。无状态容器可以连接到云端 MySQL 数据库，所有配置参数和数据都会存储到云数据库中。

当前 compose 示例：

```yaml
version: '3.8'

services:
  codex-web:
    image: wenfxl/wenfxl-codex-manager:latest
    container_name: wenfxl_codex_manager
    ports:
      - "8000:8000"
    restart: always
    environment:
      - TZ=Asia/Shanghai
      - DB_TYPE=mysql
      - DB_HOST=MySQL IP
      - DB_PORT=3306
      - DB_USER=root
      - DB_PASS=password
      - DB_NAME=wenfxl_manager
```

### Docker 部署步骤

1. 将 `docker-compose.yml` 和 `config.yaml` 放在同一目录。
2. 启动 Web 控制台容器：

```bash
docker compose up -d
```

3. 如有需要，查看日志：

```bash
docker compose logs -f
```

4. 停止容器：

```bash
docker compose down
```

5. 更新：

```bash
docker-compose pull wenfxl/wenfxl-codex-manager:latest
```

直接配置。

说明：
- `./data:/app/data` 用于持久化运行时数据、本地数据库内容和导出文件。
- Docker Web 控制台默认暴露在 `8000` 端口。
- 默认 Web 控制台密码：`admin`
- 当前 compose 文件使用镜像标签 `wenfxl/wenfxl-codex-manager:latest`。

## 在服务器上运行 Mihomo / Clash

如果你想在服务器上使用基于 Clash 的节点轮换，可以在后台运行 Mihomo（兼容 Clash Meta 的核心），并同时暴露本地 mixed 代理端口和 Clash API。

### 1. 准备工作目录

```bash
mkdir -p /opt/clash && cd /opt/clash
```

### 2. 下载 Mihomo 二进制文件

Linux x86_64 示例：

```bash
wget https://github.com/MetaCubeX/mihomo/releases/download/v1.18.1/mihomo-linux-amd64-v1.18.1.gz
gzip -d mihomo-linux-amd64-v1.18.1.gz
mv mihomo-linux-amd64-v1.18.1 mihomo
chmod +x mihomo
```

### 3. 下载由订阅转换得到的配置

```bash
wget -U "Clash-meta" -O /opt/clash/config.yaml 'YOUR_SUBSCRIPTION_CONVERTER_URL'
```

### 4. 检查 `config.yaml` 中的重要字段

检查 Mihomo 配置中的这些字段：
- `mixed-port`
- `external-controller`
- `secret`

示例：

```yaml
mixed-port: 7897
external-controller: 127.0.0.1:9097
secret: your-secret
```

然后对齐你的项目配置：

```yaml
default_proxy: "http://127.0.0.1:7897"

clash_proxy_pool:
  enable: true
  pool_mode: false
  api_url: "http://127.0.0.1:9097"
  secret: "your-secret"
  test_proxy_url: "http://127.0.0.1:7897"
```

### 5. 在后台启动 Mihomo

```bash
nohup /opt/clash/mihomo -d /opt/clash > /opt/clash/clash.log 2>&1 &
```

### 6. 停止 Mihomo

```bash
pkill mihomo
```

### 7. 多容器代理池思路

如果你使用服务器端并发注册，并希望每个 worker 使用独立的 Clash 实例，可以暴露多个本地代理端口，例如：

- `41001`
- `41002`
- `41003`

并将它们与对应的控制器 API 配对。然后填写 `warp_proxy_list` 并启用 `pool_mode: true`。

### 8. 通过 Web 控制台部署 Clash 代理集群（推荐）

旧版 shell 脚本部署方式已废弃，改为使用直接内置在 Web 控制台中的强大功能。现在你可以动态扩容、配置和路由 Mihomo（Clash）容器，无需接触命令行。

#### 第 1 步：进入代理设置
登录 Wenfxl Web 控制台，导航到 **[Network Proxy]** 标签页。

#### 第 2 步：扩容集群
找到 **Mihomo Instance Cluster Control** 面板。输入你需要的容器实例数量（例如 `5`），然后点击 **[Sync Scale]**。后端会自动为你创建并映射 Docker 容器。
*（注意：代理端口会从 41001 开始自动映射，API 端口会从 42001 开始自动映射。）*

#### 第 3 步：分发订阅
在 **Subscription Update** 区域中粘贴你的代理订阅 URL，然后点击 **[Distribute]**。系统会自动拉取节点、应用必要补丁（启用 LAN 和 API 访问），并重启实例。

#### 第 4 步：一键同步代理池
点击面板顶部紫色的 **[🔗 Sync to Exclusive Pool]** 按钮。这会自动计算新集群的内部路由地址，并将其直接连接到智能代理池以实现负载均衡。

## 输出文件

典型输出文件包括：

### JSON 文件

示例：

```text
token_user_example.com_1711111111.json
```

这些文件存储结构化 token / 凭据输出数据。

### `accounts.txt`

示例：

```text
example@gmail.com----password123
```

该文件在适用时存储本地账号与密码对。

## 故障排查

### Clash 节点切换失败
请检查：
- Clash API 是否已启用
- `clash_proxy_pool.api_url` 是否正确
- 如启用了认证，控制器 `secret` 是否正确
- `group_name` 是否匹配真实可选的代理组
- `test_proxy_url` 是否指向可工作的本地代理端口
- 黑名单是否过于严格

### 多线程代理池未按预期工作
请检查：
- `enable_multi_thread_reg: true`
- `clash_proxy_pool.enable: true`
- `clash_proxy_pool.pool_mode: true`
- `warp_proxy_list` 不为空
- 列出的每个本地代理端点实际可达
- 每个代理 / 容器都有匹配的控制器 API

### Gmail IMAP 登录失败
请检查：
- IMAP 是否已启用
- 如果需要应用专用密码，是否已启用两步验证
- 你使用的是应用专用密码，而不是普通邮箱密码

### 没有收到邮件
可能原因：
- 邮件进入了垃圾邮件
- 代理路由破坏了邮箱连通性
- 邮箱后端凭据无效
- 域名配置错误
- 后端 API 未返回预期的消息列表

### OTP 未被提取
可能原因：
- 邮件正文编码异常
- 验证码不是 6 位数字
- 消息格式不匹配提取模式
- 验证码只存在于详情端点，而不是列表视图中

### CPA 检查或补货行为异常
请检查：
- `cpa_mode.enable` 是否设置正确
- `cpa_mode.api_url` 和 `api_token` 是否正确
- `cpa_mode.threads` 对你的服务器 / API 容量而言是否设置过高
- `remove_on_limit_reached` / `remove_dead_accounts` 是否符合你的预期策略

## 安全说明

- 不要公开暴露 `db` 或 token JSON 输出。
- 邮箱管理员凭据、CPA token 和 Clash 控制器 secret 建议使用更强的密钥处理方式。
- 限制对输出目录的访问。
- 如果在团队环境中使用，请增加审计日志和权限边界。

## 使用条款与许可证

本项目是一个 **“源码可见”** 的私有项目，使用 **CC BY-NC 4.0**（Creative Commons Attribution-NonCommercial 4.0 International）许可证授权。

* **作者**：wfxl（GitHub: [wenfxl](https://github.com/wenfxl)）
* **许可证文件**：[`LICENSE`](https://github.com/wenfxl/openai-cpa/blob/master/LICENSE)
* **完整许可证**：[CC BY-NC 4.0 Legal Code](https://creativecommons.org/licenses/by-nc/4.0/legalcode)

### 🚫 严格合规与禁止商业使用
本项目在严格意义上 **不是** 自由和开源软件（FOSS）。所有用户都必须严格遵守以下准则：

1. ✅ **允许**：严格限制为个人开发者用于技术学习、代码研究和非盈利本地测试。
2. ⚠ **必须署名（BY）**：如果你复制、分发或修改此代码，**必须** 清晰标注原作者（**wfxl**），并提供此原始仓库链接。严禁移除作者版权声明并声称代码为自己所有。
3. ❌ **严格禁止（NC）**：任何个人、团队或企业都严禁将本项目（及其任何修改版本）用于任何形式的商业变现。这包括但不限于：
   - 打包为闭源、加密或隐藏代码后进行二次转售；
   - 将其部署为面向公众的付费 SaaS 服务（例如付费注册平台、token 销售站点）；
   - 将其捆绑到其他商业引流产品中。

**如果发现任何未经授权的商业使用或版权侵权行为（例如未署名），作者保留采取完整法律行动并主张经济赔偿的权利。**

> **免责声明**
> 本项目严格用于技术学习、自动化研究和教育交流。请确保你的使用方式符合当地法律法规，以及相关平台（例如 OpenAI、Cloudflare 等）的服务条款。因不当或非法使用导致的任何法律纠纷、账号封禁或资产损失，均由用户自行承担全部且唯一的责任。作者不承担任何责任或连带责任。

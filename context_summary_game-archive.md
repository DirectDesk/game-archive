# game-archive 开发上下文总结

> 用途：记录本项目的部署踩坑、当前实现状态和可复用经验，供后续开发代理或维护者快速恢复上下文。

## 项目位置与运行方式

- 本地项目：`/home/devuser/codex_work/game-archive`
- 后端：FastAPI + SQLAlchemy Async + SQLite
- 前端：Vue 3 + Vite + Tailwind CSS
- 容器服务：`game-archive`，对外端口 `8080`
- 生产部署目录（FNOS）：`/vol1/1000/docker/game-archive`
- 数据目录挂载：`/vol1/1000/docker/game-archive/data:/app/data`
- RAWG API Key 支持从 `SystemConfig.rawg_api_key`、环境变量 `RAWG_API_KEY` 或应用配置回退读取。

## 已完成的修复/功能

### RAWG 与翻译

- 术语表支持按分类优先匹配，并支持无分类兜底。
- 翻译失败静默返回原文，不阻塞 RAWG 搜索、详情和扫描流程。
- 自动翻译仅在 `SystemConfig.auto_translate=true` 时执行。
- 游戏标题翻译后保留英文标题到 `alias`。
- 已加入标题特例：
  - `AI*Shoujo` / `AI＊Shoujo` → `AI*少女` / `AI＊少女`
  - `Magical Girl Witch Trial` → `魔法少女的魔女审判`
- 开发商、发行商不再自动汉化。
- RAWG 描述、标签可自动翻译；RAWG 请求或详情失败时可创建基础游戏记录。
- RAWG 详情会从标题提取类似 `v1.1.2` 的版本号，没有版本时留空。
- RAWG 短截图 URL 会保存到 `screenshots`。

### 数据库与接口

- `Game` 已有/新增字段：`screenshots`、`version`、`original_data`、`created_at`、`play_status`。
- 应用启动时使用 SQLite `PRAGMA table_info` 检测并补充新字段，无需手动迁移旧数据库。
- `original_data` 保存翻译前的标题、别名、描述、开发商、发行商、标签和系列 JSON。
- 游戏列表搜索支持：标题、别名、开发商、发行商、系列。
- 游戏状态目标为三种：`favorite`（仅收藏）、`playing`（游玩中）、`completed`（已通关）；默认 `favorite`。
- 新增截图上传接口：`POST /api/games/{game_id}/screenshots`。
- 封面和截图均限制 `image/jpeg`、`image/png`。

### 部署与验证经验

- 已经验证腾讯翻译服务和 RAWG 连通性。
- 已同步源码到 FNOS，并曾通过复制源码到运行容器后重启完成临时验收。
- 本地 Python 语法检查和前端构建曾通过；重新验证时使用 `python3 -m compileall -q backend/app`，不要假设系统一定存在 `python` 命令。
- FNOS 上需要最终成功执行一次无缓存 `docker compose build`，避免运行容器依赖临时 `docker cp` 覆盖。
- 重建镜像后应再次检查容器内 `rawg_client.py`、翻译服务和数据库迁移版本。

## 当前未完成/需继续处理

- 前端 `frontend/src/App.vue` 的大规模 UI 改造尚未完成或尚未最终验收。目标包括：
  - 主页面原始/中文语言切换，并使用 `original_data` 显示原始 API 数据。
  - 标签过滤改为左侧可伸缩、可固定的侧栏。
  - 详情页显示版本和首次入库时间。
  - 详情页提供“更新元数据”按钮，卡片上不显示该按钮。
  - “上传自定义封面”按钮放在封面 URL 行。
  - 去掉“打开资源”，改为复制 NAS 绝对路径并提示“请在nas文件管理中打开”。
  - 截图大图预览、翻页和手动 JPG/PNG 上传。
- 应检查 `backend/app/schemas.py` 对旧数据库数据的兼容性，尤其旧状态 `archived`、`downloading` 的启动转换。
- 需要分别验收新扫描游戏和手动刷新游戏：标题、标签、描述、版本、截图、原始/中文切换。
- 需要确认 `SystemConfig` 中自动翻译开关、腾讯配置和 RAWG Key 已持久化。
- 本地代码尚未提交，完成全部修改后再提交并记录镜像版本。

## 常用验证命令

```bash
cd /home/devuser/codex_work/game-archive
python3 --version
python3 -m compileall -q backend/app
npm --prefix frontend run build
git diff --check
git status --short
```

## Python 命令说明

- 当前环境确认：`python3` 为 `/usr/bin/python3`，版本 `3.10.12`。
- `/usr/bin/python` 原先不存在。
- 创建 `/usr/bin/python -> /usr/bin/python3` 需要 root 权限；自动化工具执行 `sudo ln -s /usr/bin/python3 /usr/bin/python` 时会等待 `devuser` 密码，无法在非交互工具中输入。
- 若需要创建软链接，请在管理员终端执行：

```bash
sudo ln -s /usr/bin/python3 /usr/bin/python
```

- 如果目标已存在，先检查：

```bash
ls -l /usr/bin/python
```

不要在未确认目标的情况下使用 `ln -sf` 覆盖系统解释器。

## 重要实现注意事项

- `GameUpdate` 当前是全量模型，前端更新时必须提交完整游戏对象，否则 Pydantic 会拒绝请求。
- RAWG 翻译流程必须先保存原始快照，再修改中文字段；刷新元数据时不能清空 `original_data`。
- 开发商和发行商只保存 RAWG 原文；不要把它们加入翻译字段映射。
- 版本只能从名称识别；RAWG 没有版本信息时必须返回空字符串，不要用发布日期或其他字段代替。
- 前端上传文件时不要手动设置 `Content-Type: application/json`，应让浏览器为 `FormData` 自动设置 multipart boundary。
- 截图 URL 既可能是外部 RAWG URL，也可能是 `/data/screenshots/...` 本地静态资源，前端应兼容两种形式。
# Game Archive

轻量单用户游戏归档库，支持 RAWG / VNDB 元数据搜索、云盘链接、NAS 本地路径和后台下载。

## 项目结构

```text
game-archive/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── services.py
│   │   ├── clients/
│   │   │   └── rawg_client.py
│   │   ├── downloader.py
│   │   └── routers/
│   │       ├── games.py
│   │       ├── metadata.py
│   │       └── downloads.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.vue
│   │   ├── main.js
│   │   └── style.css
│   ├── index.html
│   ├── package.json
│   ├── postcss.config.js
│   └── vite.config.js
├── Dockerfile
├── docker-compose.yml
└── .env.example
```

## 本地开发

后端：`cd backend && pip install -r requirements.txt && uvicorn app.main:app --reload`

前端：`cd frontend && npm install && npm run dev`

## 飞牛部署

1. 将项目上传到飞牛。
2. 在 [RAWG](https://rawg.io/signup) 注册账号，国内邮箱即可，无需手机号或 2FA；个人免费额度为每月 20000 次请求。复制 `.env.example` 为 `.env`，填写 `RAWG_API_KEY`。
   RAWG 不绑定 IP，飞牛 NAS 可直接调用；国内网络偶有超时属于正常现象。
3. 按实际目录修改 `docker-compose.yml` 中 `/app/data` 和 `/vol/baidu` 左侧路径。
4. 执行 `docker compose up -d --build`。
5. 浏览器访问 `http://飞牛IP:8080`。

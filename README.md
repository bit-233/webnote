# Ubuntu Web 笔记应用

一个面向 Ubuntu 服务器的**轻量级、单机运行、无数据库依赖**的 Web 笔记应用。使用 FastAPI + 原生前端，所有笔记以 JSON 文件存储在 `data/notes` 目录。

## 功能概览
- Markdown 笔记的创建、查看、更新与删除
- 标题关键字搜索、单标签筛选，按更新时间倒序展示
- 前端实时 Markdown 预览
- 可选的单用户密码登录（设置 `NOTES_ADMIN_PASSWORD` 即启用）

## 运行方式
1. 安装依赖
   ```bash
   pip install -r requirements.txt
   ```
2. 启动服务
   ```bash
   python main.py
   # 或 uvicorn main:app --host 0.0.0.0 --port 7056
   ```
3. 浏览器访问 `http://服务器IP:7056`，即可进入前端界面。

> 默认监听 `0.0.0.0:7056`，数据保存在 `./data/notes`。首次启动会自动创建目录。

## 配置
可通过环境变量覆写默认值：

- `NOTES_HOST`：监听地址，默认 `0.0.0.0`
- `NOTES_PORT`：监听端口，默认 `7056`
- `NOTES_DATA_DIR`：数据目录，默认 `./data`
- `NOTES_ADMIN_PASSWORD`：管理密码，留空表示关闭登录验证

登录后会写入一个简单的 `notes_session` Cookie，用于保护写操作（创建/更新/删除）。

## 项目结构
```
project-root/
├── api/                # FastAPI 路由与认证
├── config.py           # 配置读取
├── data/notes/         # JSON 笔记存储目录（运行时自动创建）
├── main.py             # 应用入口
├── storage.py          # 文件存储读写封装
├── web/static/         # 前端页面与样式
└── requirements.txt
```

## 开发提示
- 可通过 `/docs` 查看交互式 API 文档。
- 如需部署为守护进程，可结合 systemd：`ExecStart=uvicorn main:app --host 0.0.0.0 --port 7056`。


# Web-Note 项目解析

## 总览
Web-Note 是一个基于 FastAPI 的单机 Markdown 笔记应用，前端使用原生 HTML/CSS/JS，数据以 JSON 文件形式保存在 `data/notes` 目录。应用默认监听 `0.0.0.0:7056`，可通过环境变量配置主机、端口、数据目录和可选的管理密码。

## 配置与入口
- **入口**：`main.py` 创建 FastAPI 应用，挂载静态资源目录 `/static` 并在启动时调用 `storage.ensure_dirs()` 保证数据目录存在。根路由返回前端 `index.html`，并暴露 `/api/config` 供前端获取是否启用登录。登录/登出接口则直接调用 `api.security` 中的逻辑。
- **配置**：`config.py` 读取 `NOTES_HOST`、`NOTES_PORT`、`NOTES_DATA_DIR` 和 `NOTES_ADMIN_PASSWORD` 环境变量，生成 `APP_CONFIG`，并统一使用 `notes_session` 作为认证 Cookie 名称。

## 认证机制
- **Token 生成**：`api/security.py` 将管理密码经 SHA-256 计算得到期望的 Token；当未配置密码时，鉴权被视为关闭。
- **鉴权装饰器**：`require_auth` 通过读取名为 `notes_session` 的 Cookie 校验 Token，不匹配则返回 401。
- **登录/登出**：`login` 在密码正确时写入 HttpOnly 的 `notes_session` Cookie；`logout` 删除同名 Cookie。所有写操作路由均通过 `Depends(require_auth)` 保护。

## 笔记存储与 API
- **数据层**：`storage.py` 将每条笔记存储为 `data/notes/<id>.json`。`create_note` 以时间戳生成 ID，并使用当前 UTC ISO 时间填充 `created_at` / `updated_at`。
- **查询**：`list_notes` 会按更新时间（或创建时间）倒序排列，可通过 `query` 过滤标题关键字，通过 `tag` 单标签过滤。
- **API 路由**：`api/notes.py` 定义 CRUD 路由：
  - `GET /api/notes`：列出全部或过滤后的笔记。
  - `GET /api/notes/{id}`：获取单条笔记，不存在返回 404。
  - `POST /api/notes`：创建笔记（需登录时鉴权）。
  - `PUT /api/notes/{id}`：更新笔记（需鉴权），不存在返回 404。
  - `DELETE /api/notes/{id}`：删除笔记（需鉴权），不存在返回 404。

## 前端逻辑
- **界面结构**：`web/static/index.html` 包含顶部搜索/登录栏、侧边笔记列表、主编辑器（标题、标签、正文）及 Markdown 预览。
- **交互**：`web/static/main.js` 负责数据绑定与事件处理：
  - 初始化时获取配置，决定是否展示登录/登出按钮。
  - 搜索框和标签过滤实时调用 `loadNotes` 以查询笔记列表。
  - `saveNote` 根据是否有 `currentId` 决定创建或更新笔记，并在 401 时提示需要登录。
  - `deleteNote` 在确认后删除当前笔记。
  - `handleLogin`/`handleLogout` 调用对应 API，成功后通过浏览器 Alert 提示。
  - `updatePreview` 使用 `marked` 库实时渲染 Markdown。

## 运行与数据
运行 `python main.py` 即可启动应用，或使用 `uvicorn main:app --host 0.0.0.0 --port 7056`。数据默认写入项目根目录下的 `data/notes`，首次启动会自动创建目录。

## 已实施的优化
- **鉴权安全**：登录校验采用恒时比较（`secrets.compare_digest`），并针对同一 IP 增加 5 分钟 5 次的登录尝试速率限制，降低暴力破解风险。
- **前端体验**：
  - 新增 Toast 轻量提示替代 Alert，支持错误、成功、信息三类提示；列表在加载和空结果时有清晰的占位文案。
  - 笔记列表展示更新时间与标签徽章，默认展示“无标签”；增加保存（Ctrl/⌘+S）与新建（Ctrl/⌘+Shift+N）快捷键提示。



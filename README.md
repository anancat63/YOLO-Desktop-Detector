# YOLO Desktop Detector (PySide6 + Ultralytics)

[中文](#中文说明) | [English](#english)

---

## 中文说明

一个可直接运行的桌面端目标检测项目，使用 `PySide6` 构建 GUI，使用 `Ultralytics YOLO` 进行推理，支持登录/注册、用户管理、图片检测、视频检测、摄像头实时检测和结果表格展示。

> 项目定位：教学演示、课程设计、毕设展示、快速搭建桌面检测原型。

### 功能特性

- 登录 / 注册
- 管理员用户管理（编辑、删除用户）
- 图片检测
- 视频检测
- 摄像头实时检测
- 识别结果表格化展示（类别、置信度、坐标）
- 配置驱动（模型、阈值、数据库、窗口参数）

### 技术栈

- Python 3.9+
- PySide6
- Ultralytics YOLO
- OpenCV
- NumPy
- SQLite（默认）/ MySQL（可选）

### 项目结构与脚本说明

```text
yolo-desktop-detector/
├─ main.py                     # 程序入口：调用 src.app.run()
├─ app_config.json             # 项目主配置（窗口/检测/数据库/类别）
├─ .env.example                # 环境变量模板（可选，主要用于 APP_CONFIG_PATH 示例）
├─ requirements.txt            # Python 依赖列表
├─ README.md                   # 项目说明文档（本文件）
│
├─ src/
│  ├─ __init__.py              # Python 包标识
│  ├─ app.py                   # 主界面与主流程（登录、检测、结果展示）
│  ├─ config.py                # 配置加载器（读取 app_config.json / APP_CONFIG_PATH）
│  ├─ database.py              # 数据库初始化与用户表 CRUD（sqlite/mysql）
│  ├─ detect_tools.py          # 检测显示相关工具函数（图像格式转换等）
│  ├─ framework.py             # YOLO 推理封装（加载模型、预测、结果解析）
│  └─ manage.py                # 用户管理窗口逻辑（管理员功能）
│
├─ ui/
│  ├─ __init__.py              # Python 包标识
│  ├─ UiMain.py                # 主界面（由 Qt Designer 转换生成）
│  ├─ Management.py            # 用户管理界面（由 Qt Designer 转换生成）
│  ├─ ui_sources_rc.py         # Qt 资源文件编译输出
│  ├─ icon/                    # 界面图标资源
│  ├─ img/                     # 界面图片资源
│  └─ design/                  # .ui 设计稿与资源源文件
│
├─ examples/                   # 示例图片
├─ weights/                    # 模型权重目录（建议放你的自定义 .pt）
└─ data/                       # 运行期数据目录（SQLite 首次运行自动创建）
```

### 配置文件说明（`app_config.json`）

> 已在配置文件中加入 `_comment` 注释字段，便于直接查看每个配置块用途。

关键配置块：

- `window`：主窗口大小和图像显示区域大小
- `detection`：模型路径、任务类型、阈值、设备
- `database`：数据库引擎选择及连接参数
- `class_names_en` / `class_names_zh`：类别名称映射（顺序必须和模型类别索引一致）

---

### 快速上手（含“导入自己的模型”）

#### 1) 创建虚拟环境并安装依赖

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

#### 2) 准备你的模型权重

把你训练好的权重文件（如 `best.pt`）放到项目的 `weights/` 目录，例如：

```text
weights/best.pt
```

#### 3) 修改检测配置（重点）

打开 `app_config.json`，修改 `detection` 和类别名：

```json
"detection": {
  "model_path": "./weights/best.pt",
  "task": "detect",
  "conf": 0.25,
  "iou": 0.7,
  "device": "auto",
  "warmup_shape": [48, 48, 3]
}
```

然后根据你的模型类别，更新：

- `class_names_en`
- `class_names_zh`

> 注意：
> 1. 数组长度要和模型类别数一致；
> 2. 顺序必须和训练时的类别索引一致（0,1,2...）。

##### 示例：导入一个 3 类模型（cat / dog / bird）

假设你的权重文件是 `weights/pets_best.pt`，训练时类别索引如下：

- `0: cat`
- `1: dog`
- `2: bird`

那么配置可写成：

```json
"detection": {
  "model_path": "./weights/pets_best.pt",
  "task": "detect",
  "conf": 0.30,
  "iou": 0.60,
  "device": "auto",
  "warmup_shape": [48, 48, 3]
},
"class_names_en": ["cat", "dog", "bird"],
"class_names_zh": ["猫", "狗", "鸟"]
```

如果你不确定类别顺序，先打开训练使用的 `data.yaml`，以 `names` 的顺序为准填入 `class_names_*`。

#### 4) 运行项目

```bash
python main.py
```

默认数据库为 SQLite，首次运行会自动创建 `data/app.db`，并初始化管理员账号：

- 用户名：`admin`
- 密码：`admin123`

#### 5) 在界面中测试识别

- 点击“图片检测”选择测试图像
- 点击“视频检测”选择视频文件
- 点击“摄像头检测”进行实时识别

若表格能显示类别、置信度和坐标，说明模型接入成功。

---

### 数据库配置（SQLite / MySQL）

默认使用 SQLite：

```json
"database": {
  "engine": "sqlite",
  "sqlite_path": "./data/app.db"
}
```

若切换到 MySQL：

1. 安装并启动 MySQL，创建数据库（如 `yolo_app`）
2. 安装驱动：

```bash
pip install pymysql
```

3. 修改配置：

```json
"database": {
  "engine": "mysql",
  "mysql": {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "your_password",
    "database": "yolo_app",
    "charset": "utf8mb4"
  }
}
```

---

### 常见问题（FAQ）

**Q1：报错 `No module named 'ui'`？**  
请从项目根目录运行 `python main.py`，不要直接运行 `python src/app.py`。

**Q2：模型文件找不到？**  
检查 `detection.model_path` 路径是否正确，确认权重文件存在。

**Q3：类别显示错乱？**  
检查 `class_names_en/class_names_zh` 的数量和顺序是否和模型类别索引一致。

**Q4：MySQL 无法连接？**  
确认服务已启动、账号密码正确、数据库已创建，并将 `database.engine` 设置为 `mysql`。

**Q5：摄像头打不开？**  
确认摄像头未被其他程序占用，并在系统中授予摄像头权限。

---

## English

A ready-to-run desktop object detection project using `PySide6` for GUI and `Ultralytics YOLO` for inference. It supports login/register, user management, image detection, video detection, real-time webcam detection, and tabular result display.

> Positioning: teaching demos, coursework/final projects, and quick desktop detection prototyping.

### Features

- Login / Register
- Admin user management (edit/delete users)
- Image detection
- Video detection
- Webcam real-time detection
- Detection result table (class, confidence, bbox)
- Configuration-driven architecture (model, thresholds, DB, window)

### Tech Stack

- Python 3.9+
- PySide6
- Ultralytics YOLO
- OpenCV
- NumPy
- SQLite (default) / MySQL (optional)

### Project Structure & Script Responsibilities

```text
yolo-desktop-detector/
├─ main.py                     # Entry point: calls src.app.run()
├─ app_config.json             # Main project config (window/detection/database/classes)
├─ .env.example                # Optional env template (mainly APP_CONFIG_PATH example)
├─ requirements.txt            # Python dependencies
├─ README.md                   # Project documentation (this file)
├─ LICENSE                     # License
│
├─ src/
│  ├─ __init__.py              # Python package marker
│  ├─ app.py                   # Main UI and workflow (login, detection, rendering)
│  ├─ config.py                # Config loader (app_config.json / APP_CONFIG_PATH)
│  ├─ database.py              # DB init + user CRUD (sqlite/mysql)
│  ├─ detect_tools.py          # Detection utility helpers (image conversion, etc.)
│  ├─ framework.py             # YOLO wrapper (load model, predict, parse result)
│  └─ manage.py                # User-management window logic (admin features)
│
├─ ui/
│  ├─ __init__.py              # Python package marker
│  ├─ UiMain.py                # Main window UI (generated from Qt Designer)
│  ├─ Management.py            # Management UI (generated from Qt Designer)
│  ├─ ui_sources_rc.py         # Compiled Qt resource module
│  ├─ icon/                    # UI icon assets
│  ├─ img/                     # UI image assets
│  └─ design/                  # .ui source files and resource source files
│
├─ examples/                   # Example images
├─ weights/                    # Model weights directory (recommended for your custom .pt)
└─ data/                       # Runtime data directory (auto-created for SQLite)
```

### Config Notes (`app_config.json`)

> `_comment` fields have been added in `app_config.json` to explain what each section does.

Key blocks:

- `window`: Main window and preview area sizes
- `detection`: Model path, task type, thresholds, and device
- `database`: DB engine selection and connection options
- `class_names_en` / `class_names_zh`: Class-name mapping (must match model class indices)

---

### Quick Start (Including Custom Model Import)

#### 1) Create virtual environment and install dependencies

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

#### 2) Put your model weights into `weights/`

Copy your trained weights file (e.g., `best.pt`) to:

```text
weights/best.pt
```

#### 3) Update detection config (critical step)

Edit `app_config.json` and update `detection` and class names:

```json
"detection": {
  "model_path": "./weights/best.pt",
  "task": "detect",
  "conf": 0.25,
  "iou": 0.7,
  "device": "auto",
  "warmup_shape": [48, 48, 3]
}
```

Then update:

- `class_names_en`
- `class_names_zh`

Important:
1. Array length must equal your number of classes.
2. Order must match your training class index order (0,1,2...).

##### Example: import a 3-class model (cat / dog / bird)

Assume your weight file is `weights/pets_best.pt`, and your training class indices are:

- `0: cat`
- `1: dog`
- `2: bird`

Then your config can be:

```json
"detection": {
  "model_path": "./weights/pets_best.pt",
  "task": "detect",
  "conf": 0.30,
  "iou": 0.60,
  "device": "auto",
  "warmup_shape": [48, 48, 3]
},
"class_names_en": ["cat", "dog", "bird"],
"class_names_zh": ["猫", "狗", "鸟"]
```

If you are unsure about class order, open your training `data.yaml` and copy the `names` order into `class_names_*`.

#### 4) Run

```bash
python main.py
```

By default, SQLite is used. On first run, `data/app.db` is auto-created and a default admin account is initialized:

- Username: `admin`
- Password: `admin123`

#### 5) Validate detection in GUI

- Click “Image Detection” and choose a test image
- Click “Video Detection” and choose a video
- Click “Camera Detection” for real-time inference

If class/confidence/bbox entries appear in the table, your custom model integration works.

---

### Database Configuration (SQLite / MySQL)

Default SQLite mode:

```json
"database": {
  "engine": "sqlite",
  "sqlite_path": "./data/app.db"
}
```

To switch to MySQL:

1. Install/start MySQL and create a database (e.g., `yolo_app`)
2. Install driver:

```bash
pip install pymysql
```

3. Update config:

```json
"database": {
  "engine": "mysql",
  "mysql": {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "your_password",
    "database": "yolo_app",
    "charset": "utf8mb4"
  }
}
```

---

### FAQ

**Q1: `No module named 'ui'` error?**  
Run from project root with `python main.py`. Do not run `python src/app.py` directly.

**Q2: Model file not found?**  
Check `detection.model_path` and confirm the weight file exists.

**Q3: Wrong class labels?**  
Check class-name arrays for count and order against your model indices.

**Q4: MySQL connection failed?**  
Ensure MySQL service is running, credentials are correct, DB exists, and `database.engine` is set to `mysql`.

**Q5: Webcam cannot open?**  
Ensure no other app is using camera and OS camera permission is granted.

---

## License

MIT License. See `LICENSE` for details.

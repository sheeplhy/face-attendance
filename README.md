# 轻量化人脸考勤工具

这是我使用 Python、OpenCV 和 Tkinter 完成的个人练习项目。程序读取摄像头画面，使用 Haar 级联分类器检测正面人脸，并在输入姓名、点击“打卡”后，将姓名与时间追加写入本地文本文件。

> 当前版本只实现**人脸检测辅助打卡**，不进行身份识别或活体检测，不适合直接用于真实单位的正式考勤。

## 功能

- 尝试打开摄像头 `0` 和 `1`
- 摄像头不可用时，尝试读取本地 `test.jpg`
- 视频源全部不可用时显示合成提示画面
- 灰度转换与 5×5 高斯模糊预处理
- Haar 正面人脸检测与实时标注
- Tkinter 姓名输入、打卡按钮和状态提示
- 将姓名和时间追加写入 `attendance_records.txt`

## 技术栈

- Python
- OpenCV
- Tkinter / ttk
- Pillow
- NumPy

## 运行

建议先创建虚拟环境，再安装依赖：

```bash
python -m venv .venv
```

Windows PowerShell：

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

Linux / macOS：

```bash
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

运行后输入姓名，将正面人脸放在摄像头画面中，再点击“打卡”。记录会写入仓库目录下的 `attendance_records.txt`。

## 项目结构

```text
face-attendance/
├── main.py              # 应用入口、检测流程与 Tkinter 界面
├── requirements.txt     # Python 依赖
├── README.md            # 项目说明
└── .gitignore           # 忽略本地记录、测试图片和缓存
```

## 数据与隐私

- `attendance_records.txt`、`test.jpg` 和本地数据库已加入忽略规则，不会随代码提交。
- 当前版本不保存摄像头帧和人脸特征，但姓名与考勤时间仍属于个人信息。
- 在真实场景使用前，需要补充身份验证、活体检测、授权同意、访问控制、加密存储、数据删除和准确性评估。

## 当前限制

- 姓名由用户手动输入，不能证明镜头前的人就是该姓名对应的人。
- 没有活体检测，照片或视频回放可能通过检测。
- Haar 检测对侧脸、遮挡、逆光和远距离人脸的适应性有限。
- 本地文本记录没有数据库查询、去重、权限和防篡改能力。

## 后续计划

- 增加重复打卡限制和历史记录查询
- 使用 SQLite 管理考勤记录
- 将视频采集与检测移到工作线程
- 评估更现代的人脸检测方案
- 在获得授权的前提下研究身份比对与活体检测
- 增加异常处理、日志和测试用例

## 技术文章

[我用 Python 与 OpenCV 做了一个轻量化人脸考勤工具](https://sheeplhy.github.io/posts/opencv-face-attendance/)

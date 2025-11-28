# 贡献指南

感谢你对「浅听音乐格式转换器」的关注与贡献！为确保协作高效与代码质量，请遵循以下指南。

## 开发环境
- Python 3.10+（建议与项目一致的 3.13.x）
- 建议使用虚拟环境：`python -m venv myenv`
- 依赖安装：`pip install -r requirements.txt`

## 运行与调试
- 启动应用：`python main.py`
- 日志位置：`logs/converter.log`
- 如需重建虚拟环境：
  - Windows PowerShell：
    - 移除旧环境：`Remove-Item -Recurse -Force .\myenv -ErrorAction SilentlyContinue`
    - 创建新环境：`python -m venv .\myenv`
    - 激活：`./myenv/Scripts/activate`
    - 安装依赖：`pip install -r requirements.txt`

## 代码规范
- 遵循 PEP 8
- 变量与函数命名语义化，避免缩写
- 适当添加中文注释，解释关键逻辑与边界处理
- 模块化与复用，避免重复代码

## 架构约定
- 转换器：实现于 `converters/`，遵循 `core/base.py` 的抽象接口
- 注册机制：使用 `core/registry.py` 管理格式到转换器的映射
- 工厂模式：通过 `core/factory.py` 创建对应转换器实例
- GUI：界面位于 `gui/`，线程工作者在 `gui/workers.py`
- 配置：由 `config/settings.py` 管理，存储于用户目录

## 提交规范
- 分支：功能使用 `feat/*`，修复使用 `fix/*`
- 提交信息（示例）：
  - `feat(gui): 新增批量转换进度展示`
  - `fix(core): 关闭时安全处理当前转换线程`
- 在提交前请确保：
  - 不提交 `input/`、`output/`、`logs/`、虚拟环境与打包产物（根级 `.gitignore` 已配置）
  - 代码能正常启动并退出，无异常

## 问题反馈与 PR
- 提交 Issue 时请包含：环境信息、复现步骤、预期与实际行为、日志片段
- 提交 PR 前请自测并确保与现有架构一致

## 许可证与声明
- 项目采用 MIT 许可证（见根目录 `LICENSE`）
- 请合法使用，尊重版权与服务协议；风险自负

感谢你的贡献！

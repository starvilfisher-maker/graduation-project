# GitHub 与 Codex 云端配置

本仓库是研究文档与程序的共同来源。GitHub保存版本，Codex云端从仓库准备独立工作环境。云端基础环境用于阅读、修改和验证项目；它不代表已训练出模型，也不默认提供深度学习GPU。

## 仓库设置

- 仓库：<https://github.com/starvilfisher-maker/graduation-project>
- 主分支：`main`
- 首先阅读：`README.md`、`AGENTS.md`、`docs/08-delivery-status.md`
- 数据、模型权重、学校原始模板不在本次公开发布范围。

## 可复用的基础环境

准备 Python 3.11；也可使用通过检查的更新版本。基础依赖仅为Python标准库，无需API密钥、数据库或Web服务。

安装/验证入口：

```bash
bash scripts/setup_codex.sh
python3 scripts/check_environment.py
```

若电脑默认 `python3` 版本过低，先选择已有的3.10+解释器，或在独立环境中准备3.11；可通过 `PYTHON_BIN=/path/to/python3 bash scripts/setup_codex.sh` 指定。不要依赖某个人电脑上的绝对路径。

基础环境完成的判断是：项目与配置检查通过、数学指标测试通过，且能读取完整研究文档。TensorFlow安装、真实数据核验、模型前向/反向验证属于下一层训练环境任务。

## 当前界面的配置方法

根据2026年10月13日核对的[OpenAI官方云环境说明](https://learn.chatgpt.com/docs/environments/cloud-environments)，可在网页或桌面应用进入“工作位置→云端→选择环境”，创建或选择环境，关联本GitHub仓库。也可从设置中的Codex Cloud环境管理进入。

创建时让环境准备Python并运行本仓库的验证入口；查看设置报告，解决失败后保存并发布。只有出现环境已发布状态，才算完成可复用云端环境配置。仓库里出现此说明文件、保存草稿或GitHub推送成功，都不等于云端发布成功。

若已有本项目的设置会话或环境，应继续完善该环境，避免重复创建。可将以下文字用于**该项目环境的设置对话**：

> 为 starvilfisher-maker/graduation-project 准备基础开发环境。读取 README.md 和 AGENTS.md，使用 Python 3.11 或兼容版本，在仓库根目录运行 bash scripts/setup_codex.sh 与 python3 scripts/check_environment.py。当前只需研究文档、配置和数学指标检查，不下载真实数据、不运行完整训练、不额外安装 TensorFlow。报告解释器版本、测试结果和未完成项；基础检查通过后将环境准备为可发布状态。

发布后开启的新工作会话应先检查仓库版本与AGENTS约定。正式研究成果仍要提交到GitHub，不能只保存在某次云会话文件系统中。

## 后续训练环境

正式模型实现前，再准备TensorFlow与读取图像/病例表、统计绘图所需依赖，记录确切版本，并在Linux云端和Mac本地分别测试。Metal是Mac可选路径，不安装到Linux环境。

先测一次小批量前向/反向与数据读取，记录设备、内存、耗时，再决定在哪里完成正式训练。若环境只有CPU，可以继续做文档、数据核对与单元测试；不要把云端名称理解为已获GPU。需要外部算力时再按实际资源选择，不预先购买服务。

## 网络与凭据

当前基础检查无需联网。GitHub连接与检出由平台负责。今后安装Python依赖时按需要开放官方包管理域名；下载数据时依据TCIA实际下载链接设置必要访问。不要为了基础检查开放不相关服务，也不要在仓库提交Token。

## 发布与验收记录

实际完成状态以[交付状态](08-delivery-status.md)为准。应分别记录GitHub提交、自动检查、云端环境是否发布以及云端实测结果。某项因账户权限、登录或界面不可用而未完成时，明确记录具体阻碍，不以本地通过替代云端验证。

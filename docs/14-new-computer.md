# 新电脑恢复指南

更新日期：2026年11月6日。目标是在另一台Windows或Mac上恢复代码、研究上下文与本地文稿，让新的agent无需原聊天记录即可接续。尚未实际在目标Windows机器运行；以下使用现有脚本的跨平台命令，依赖和硬件需在目标机检查。

## 1. 先取回仓库

安装Git后，在自己选择的工作目录运行：

```text
git clone https://github.com/starvilfisher-maker/graduation-project.git
cd graduation-project
git status -sb
git log -1 --oneline
```

已有克隆时先检查本地修改，保存自己的工作后再执行 `git pull --ff-only`；如果提示分叉，不使用强制覆盖或硬重置，先核对两端改动。也可用GitHub Desktop克隆。网页“Download ZIP”能获得文件，但不保留本地Git仓库信息，后续持续协作优先用克隆。

在新agent中选择这个项目文件夹，让它先读取 `AGENTS.md` 和 [交接说明](13-agent-handoff.md)。不用复制旧电脑的虚拟环境、缓存、账号或凭据。公开仓库可直接克隆，后续推送需要在新电脑单独登录你自己的GitHub账号。

## 2. 恢复完整Word及参考材料

**GitHub不包含完整Word、模板、PDF和Excel。**从微信已经传输的资料中取回整个 `v1`；如果仅传输了Word，还需取回其余子目录。把它放在仓库根目录下，保留结构：

```text
graduation-project/
├── AGENTS.md
├── README.md
├── docs/
├── configs/
├── src/
└── v1/                         本地资料，已被Git忽略
    ├── 00_文件夹使用说明.md
    ├── 01_开题报告/
    ├── 02_参考文献/
    ├── 03_外文翻译原稿/
    └── 04_模板与核验记录/
```

整包有30个交付文件（不计系统隐藏文件），其中21篇文献PDF，另有同文献[1]相同的英文原稿副本。以包内清单为依据，不能只看文件数量判断传输完整。目录结构用于维持Excel和BibTeX的相对附件链接。

Windows PowerShell可核对Word：

```powershell
Get-FileHash -Algorithm SHA256 -LiteralPath '.\v1\01_开题报告\基于U-Net的乳腺超声病灶分割研究_开题报告含文献综述与外文翻译.docx'
```

归档稿哈希见[交接说明](13-agent-handoff.md)。有导师后续修订时哈希变化是正常的，应保存归档版并确认当前工作稿，不能为了匹配哈希撤销修改。

完整包核对：`v1/04_模板与核验记录/文件完整性清单.csv` 有29条记录，字段为 `相对路径`、`字节数`、`SHA-256`，路径以v1为根，清单不包含自身。可让agent逐项核对文件存在、字节数和哈希；核验过程只读。归档后修改过文件则标记“与归档不同”并核查版本，不直接判成损坏。

打开Word后检查字体替换、引用上标、公式、分页、译文扉页与附件显示；历史44页不保证在不同软件上完全相同。检查Excel能否打开本地PDF链接。模板保持只读，已有稿件修改前先备份。包内完整性清单描述原归档；新版本另留记录，不将旧清单悄悄改成新版本。

## 3. 研究数据与核验记录需另外恢复

v1是写作资料包，不含原始病例图像、病例表或数据图册。若仅修改开题稿，先恢复v1即可；若继续实验，还需从原电脑私下复制下列资料，或者按官方入口重新下载并重新审计。

| 仓库根目录下的本地位置 | 用途 |
| --- | --- |
| `data/raw/BrEaST-v1/` | 实际原图、掩码和病例表；目录内容以审计程序识别规则为准 |
| `data/audit/source_records/` | 原下载来源与文件校验记录 |
| `data/audit/decoded_20261014_v1/` | 已有审计汇总、病例表及文件清单 |
| `reports/data-review-20261014-v1/` | 图册、总览、助手实际检查范围与浏览验证记录 |

历史首查目录可一并保留，但当前技术结论以显式 `breast_v1` 读取规则的记录为准。复制旧审计后，核查原文件、路径、代码哈希与环境；旧机器路径或代码变化可能需要新审计。不要修改旧证据假装已经在新机器运行。缺失记录时可在新的输出目录重建，明确这是新运行，不能凭公开汇总补造逐病例结果。

这些资料不进公共Git仓库。`.gitignore`防止常规误提交，但不能保护强制添加或已经跟踪的文件；提交前仍检查 `git diff --cached --name-only`。

## 4. Windows上运行当前基础检查

先安装Python 3.11（基础工具支持3.10+，此处统一举3.11的例子），在仓库根目录的PowerShell运行。使用虚拟环境解释器的完整相对路径，无需修改系统脚本执行策略：

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e '.[audit]'
$env:PYTHONPATH = (Join-Path (Get-Location).Path 'src')
.\.venv\Scripts\python.exe scripts/check_environment.py
.\.venv\Scripts\python.exe -m compileall -q src scripts
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe scripts/check_project.py
```

若Python启动器找不到3.11，先确认已安装版本与解释器位置，不能假定上述路径可用。安装审计依赖需要联网；基础项目检查只依赖标准库，但没有NumPy、Pillow、openpyxl时部分测试会跳过，不能把“基础通过”写成“全部审计测试通过”。

## 5. Mac/Linux上的等价检查

在已有兼容Python的条件下运行：

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[audit]'
PYTHON_BIN=.venv/bin/python bash scripts/setup_codex.sh
```

上述命令都不会下载真实数据或安装TensorFlow。基础环境通过不表示训练环境、GPU或Metal已验证。正式模型环境另行建立、实测后锁定版本；不要将Mac特有依赖原样复制到Windows。

有真实数据后，现有审计与图册命令见[预处理核对](11-preprocessing-and-qc.md)。在Windows将命令中的 `python3` 换成 `.\.venv\Scripts\python.exe`；每次选择新的输出目录。尚无完整训练命令，不要照规划接口直接运行。

## 6. 可以直接交给新agent的接续说明

```text
请接续此仓库的《基于U-Net的乳腺超声病灶分割研究》。先读AGENTS.md、README.md、docs/08-delivery-status.md、docs/13-agent-handoff.md和docs/14-new-computer.md，再按当前任务阅读数据、统计协议和配置。

请先检查Git版本、本地是否有完整v1资料包，以及当前Word是否包含用户或导师的新修改。用中文简要说明已恢复哪些材料、哪些尚缺，不要求我重新复述仓库已有背景。不要改原模板，不要覆盖更新稿，不要上传个人文稿、文献PDF或病例数据。

开题正文、综述、21篇参考文献和BrEaST节译已有本地成稿，但正式毕业论文结果尚未完成。数据技术审计已完成；人工复核、最终纳入、患者划分、TensorFlow模型及正式训练仍待完成。所有计划参数尚待冻结。

我基本掌握Python、R、SPSS，医学和深度学习基础有限。请按可验收的小步骤协作，解释术语及统计含义，不安排日历。最近逐节讲解到2.3；如果我说“下一部分”，从3.1开始，每次只讲一节。只有我要求推进研究时，才进入下一项未完成的实施工作。若要修改Word，先阅读实际原文和模板，备份后编辑并检查渲染；缺少原稿不能凭摘要重造。

先完成材料与版本核对，再依据我本次具体要求继续。每次交付同步更新实际状态、文献/配置对应关系和下一步，使后续agent也能接续。
```

## 7. 恢复完成的验收

- 能读到仓库协议、21篇公开书目、当前状态及下一项任务；不依赖旧聊天才能理解方案。
- 能找到并打开当前Word、只读模板、Excel与对应PDF；缺失项被明确记录。
- 数据实施前确认原始资料及证据可访问，不把v1当作训练数据包。
- 目标机器检查记录说明Python版本、通过/跳过的测试与未验证事项。
- 训练状态仍据实标记；GitHub更新、云端环境发布、正式训练分别核实。

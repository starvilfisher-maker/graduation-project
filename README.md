# 基于 U-Net 的乳腺超声病灶分割研究

本项目面向应用统计学本科毕业论文，使用 BrEaST 公开数据集和标准二维 U-Net，研究损失函数与数据增强对病灶分割效果、训练稳定性及不同病例表现的影响。

当前已进入**论文逐步实施与首轮数据核对**。本地已取得官方数据并进行首次自动清点，完整人工质检、正式读取规则、患者划分、训练程序与模型实验仍待完成。仓库中的参数是拟采用的设计，不是实验结论；代码测试通过也不代表模型已经有效。

开始逐步完成论文，请先读[论文执行与学习路线](docs/09-guided-thesis-roadmap.md)。本轮实际发现和读取限制见[数据首轮核对记录](docs/10-data-first-pass.md)。

## 从这里阅读

| 文档 | 回答的问题 |
| --- | --- |
| [课题分析](docs/01-topic-analysis.md) | 题目研究什么，需要哪些医学与模型知识，应用统计学能贡献什么 |
| [数据处理规范](docs/02-data-protocol.md) | 下载后怎样核对文件、区分标注、划分患者并处理图像 |
| [实验与统计方案](docs/03-experiment-and-statistics.md) | 四组对照如何公平实施，怎样计算指标、比较差异、分析失败 |
| [论文实现流程](docs/04-implementation-workflow.md) | 每一步的输入、操作、输出、代码模块和验收标准 |
| [开题与论文写作依据](docs/05-proposal-writing.md) | 如何将方案写入学校模板，怎样组织综述、论文和答辩 |
| [Codex 云端配置](docs/06-codex-cloud.md) | 如何从本仓库创建可复用云端环境，区分代码验证与模型训练 |
| [资料与来源](docs/07-sources.md) | 核实过的原始资料，以及继续检索文献的方法 |
| [当前交付状态](docs/08-delivery-status.md) | 哪些工作已完成，哪些仍待实现或验证 |
| [论文执行与学习路线](docs/09-guided-thesis-roadmap.md) | 每一步做什么、交付什么、写入论文哪里；第一课如何读懂图像与掩码 |
| [数据首轮核对记录](docs/10-data-first-pass.md) | 实际文件清点与通道编码发现，哪些核对仍未完成 |

## 研究主线

```mermaid
flowchart TD
    A[官方图像 标注 病例表] --> B[清点 质量核对 病例清单]
    B --> C[按患者固定训练 验证 测试划分]
    C --> D[统一尺寸 归一化 仅训练集增强]
    D --> E[标准 U-Net 四组对照 每组三个种子]
    E --> F[验证集早停与统一规则选择阈值]
    F --> G[锁定方案后逐病例测试]
    G --> H[配对比较 稳定性 子组与失败分析]
    H --> I[论文图表 结论 限制 可复现材料]
```

| 方案 | 训练损失 | 训练增强 |
| --- | --- | --- |
| A | BCE | 无 |
| B | 0.5 BCE + 0.5 Dice loss | 无 |
| C | BCE | 有 |
| D | 0.5 BCE + 0.5 Dice loss | 有 |

所有组共用患者划分及训练种子 17、42、2026，共12次正式训练。主比较预设为 D−A，其余对照用于解释两项训练策略的作用。完整设计见[实验协议](docs/03-experiment-and-statistics.md)，机器可读建议值见[实验配置](configs/experiment_plan.json)。

## 立即可运行的检查

需要 Python 3.10 或更新版本。基础检查只使用标准库，不安装 TensorFlow，不下载数据，不运行正式训练。

```bash
bash scripts/setup_codex.sh
python3 scripts/check_environment.py
```

这些命令检查目录与配置，执行二值指标和数据关联测试。有 NumPy、Pillow、openpyxl 时还执行相应图像/表格审计测试；缺少可选依赖时明确跳过这些测试。完整 U-Net 和训练流程仍按实现文档逐步建设。

已有官方本地数据及审计依赖后，可执行实际可用的首轮审计命令（每次使用新的输出目录）：

```bash
python3 scripts/audit_breast.py --raw-dir data/raw/BrEaST-v1 --output-dir data/audit/my_first_audit
```

它保守地标记尚未定义读取规则的透明度和彩色通道，当前真实数据会报告待处理项并返回非零状态；这表示尚不满足自动放行条件，不表示这些病例应被排除。该脚本不生成患者划分，也不训练模型。所需依赖、检查覆盖及进一步解释见[首轮记录](docs/10-data-first-pass.md)。

## 项目组织

```text
docs/                    研究方案与实现说明
configs/                 拟采用的实验配置
src/breast_unet/          基础指标代码 后续扩展训练模块
scripts/                 项目与环境检查
tests/                   数值和边界条件测试
data/                    数据存放规范 原始文件不进版本库
reports/                 结果产出规范 当前无正式实验结果
.github/workflows/       基础自动检查
AGENTS.md                本地和云端 Codex 的项目约定
```

## 使用边界

- 本课题评价目标病灶区域的分割，不以分割成绩代替良恶性诊断准确率。
- 官方资料报告256例，其中4例正常。最终纳入数量必须以实际下载和质量核对为准。
- 标注是参考答案，并不意味着临床边界毫无不确定性。
- 数据、权重、个人学校材料与本机环境均不随本次提交上传。引用公开数据时保留原始出处和许可说明。
- 所有研究文档按逻辑步骤组织，不包含日历或周计划。

数据入口：[TCIA Breast-Lesions-USG](https://www.cancerimagingarchive.net/collection/breast-lesions-usg/)。

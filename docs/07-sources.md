# 资料与来源

本页是研究设计的初始阅读清单，不是已经满足学校数量要求的最终参考文献表。正式综述还需系统检索、阅读全文、核对作者与出版信息，并按学校模板统一引用。核对日期为2026年10月13日。

## 直接支撑本课题的原始资料

1. **Ronneberger O, Fischer P, Brox T. U-Net: Convolutional Networks for Biomedical Image Segmentation. 2015.** [作者论文](https://arxiv.org/abs/1505.04597)。用于理解编码器、解码器、跳跃连接及医学图像分割；本项目采用明确记录的现代同尺寸实现，不声称逐项复制原论文所有设置。
2. **Pawłowska A 等. Curated benchmark dataset for ultrasound based breast lesion analysis. Scientific Data, 11, 148, 2024.** [原文](https://www.nature.com/articles/s41597-024-02984-z)，[DOI](https://doi.org/10.1038/s41597-024-02984-z)。用于核实BrEaST数据构成、标注目标、病例字段及局限。
3. **TCIA Breast-Lesions-USG 数据集合，Version 1.** [官方入口](https://www.cancerimagingarchive.net/collection/breast-lesions-usg/)，数据DOI：[10.7937/9WKK-Q141](https://doi.org/10.7937/9WKK-Q141)。数据引用与数据论文引用分别保留；版本与实际下载文件还需下载时再次确认。

## 评价方法与近期文献线索

下面列出核实过题名、年份与来源入口的候选资料。网页检索和摘要阅读不等于完成全文精读；不从摘要推断没有报告过的实验结论。

| 资料 | 年份 | 对本课题的用途 | 原始入口 |
| --- | --- | --- | --- |
| Metrics reloaded: recommendations for image analysis validation | 2024 | 根据任务目标选择指标，理解指标解释边界 | [Nature Methods](https://www.nature.com/articles/s41592-023-02151-z) |
| Understanding metric-related pitfalls in image analysis validation | 2024 | 讨论空目标、目标大小及汇总方法可能造成的误解 | [Nature Methods](https://www.nature.com/articles/s41592-023-02150-0) |
| BUS-UCLM: Breast ultrasound lesion segmentation dataset | 2025 | 了解其他数据集的标注方式与患者多图问题；不代表本课题改用该数据 | [Scientific Data](https://www.nature.com/articles/s41597-025-04562-3) |
| A foundation generative model for breast ultrasound image analysis | 2026 | 作为领域发展趋势的候选阅读；不将大模型加入当前基础实验 | [Nature Biomedical Engineering](https://www.nature.com/articles/s41551-026-01639-1) |

这组候选与BrEaST论文提供了近期阅读起点。最终应按学院对“近三年”的口径、全文相关性和实际引用情况取舍，不能仅为凑数列入。

## 后续检索与阅读记录

中文检索词可组合“乳腺超声＋病灶分割”“U-Net＋损失函数”“医学图像＋数据增强”“图像分割＋评价指标”。英文可用 breast ultrasound segmentation、U-Net、loss function、data augmentation、small dataset、segmentation evaluation。优先寻找原始论文和可靠综述，核对出版信息，不直接采信二次转载的成绩表。

阅读表至少包含题名、作者、年份、DOI/稳定链接、研究任务、数据集、样本与患者数、划分方式、网络、损失、增强、指标、主要发现、限制和本课题拟引用位置。没有公开说明的信息标记“未报告”，不要补造。不同数据集、不同划分上的Dice不能直接视为公平排名。

围绕以下缺口补充后续文献：传统超声分割方法、U-Net改进的代表工作、损失设计、医学图像增强、小样本评价和国内相关研究。当前清单不足模板要求的完整文献数量，后续需要继续补充并在正文中真实引用。

## 工程官方资料

- [TensorFlow 安装说明](https://www.tensorflow.org/install/pip)：训练环境选版本时再次核查，当前未安装和验证TensorFlow。
- [Apple TensorFlow Metal 插件](https://developer.apple.com/metal/tensorflow-plugin/)：Mac可选加速路径，实际兼容性和耗时以试跑为准。
- [Codex Cloud 环境](https://learn.chatgpt.com/docs/environments/cloud-environments)：当前云环境创建、准备、发布与复用方式。

## 学校模板来源

使用用户提供的《2027届开题报告（含文献综述、外文翻译）模板解读》核对结构与篇幅要求。原始Word仅只读分析，没有上传公开仓库。本页也不包含用户姓名、学号或导师个人资料。正式提交时使用学校原模板及最新通知。

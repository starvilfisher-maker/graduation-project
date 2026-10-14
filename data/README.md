# 数据存放说明

从 [TCIA Breast-Lesions-USG](https://www.cancerimagingarchive.net/collection/breast-lesions-usg/) 获取图像与标注包、病例表，引用官方数据及数据论文。2026年10月14日本地已下载并完成首次自动清点，完整质检及训练读取规则仍待完成。数据文件不随GitHub同步，新检出的项目需自行从官方入口取得文件。

建议本地结构：`raw/` 保存原始包与解压文件；`manifests/` 保存清点和患者划分；`processed/` 保存必要的确定性中间结果。上述内容默认被 Git 忽略。

不要修改原始文件。不要把缺少掩码直接认定为正常，不要混淆 tumor 与 other 标注。详细规则见[数据协议](../docs/02-data-protocol.md)。

本地原始数据位于`raw/BrEaST-v1/`，原始图像子目录和病例表保留官方文件名。下载来源与SHA-256位于`audit/source_records/`。首轮自动审计输出位于`audit/initial_20261014/`，后续运行使用新目录保留原记录。实际结果及限制见[数据首轮核对记录](../docs/10-data-first-pass.md)。

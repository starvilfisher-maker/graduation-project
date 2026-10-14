# 数据存放说明

从 [TCIA Breast-Lesions-USG](https://www.cancerimagingarchive.net/collection/breast-lesions-usg/) 获取图像与标注包、病例表，引用官方数据及数据论文。当前尚未下载和核对真实数据。

建议本地结构：`raw/` 保存原始包与解压文件；`manifests/` 保存清点和患者划分；`processed/` 保存必要的确定性中间结果。上述内容默认被 Git 忽略。

不要修改原始文件。不要把缺少掩码直接认定为正常，不要混淆 tumor 与 other 标注。详细规则见[数据协议](../docs/02-data-protocol.md)。

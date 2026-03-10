# EPUB 繁体转简体转换器

将 EPUB 电子书中的**繁体中文**转换为**简体中文**，保留原有目录、样式与结构，输出新 EPUB 文件。

---

## 功能

- **单本转换**：指定一个 EPUB，输出为 `原名_simplified.epub` 或自定义路径
- **批量转换**：对目录下所有 `.epub` 一次性转换（自动跳过已带 `_simplified` 的文件）
- **内容范围**：转换正文 HTML、导航（Nav）、NCX 目录及书籍标题等元数据中的繁体字
- **不转换**：`<script>`、`<style>` 内内容不参与繁简转换，避免破坏代码
- **转换规则**：默认使用 OpenCC `tw2s`（台湾繁体 → 大陆简体），可改为 `t2s`（通用繁体 → 简体）

---

## 环境要求

- Python 3.6+
- 依赖见下方「安装」

---

## 安装

```bash
pip install opencc-python-reimplemented EbookLib
```

或使用 requirements（若项目中有）：

```bash
pip install -r requirements.txt
```

---

## 使用方法

### 转换单个文件

```bash
# 输出为 原文件名_simplified.epub
python convert.py 你的书.epub

# 指定输出路径
python convert.py 你的书.epub -o 输出路径/简体版.epub
```

### 批量转换

```bash
# 转换目录下所有 .epub（跳过已包含 _simplified 的文件）
python convert.py -d ./书籍目录/
```

### 查看帮助

```bash
python convert.py -h
```

---

## 参数说明

| 参数 | 说明 |
|------|------|
| `input` | 输入的 EPUB 文件路径（单文件模式时使用） |
| `-o`, `--output` | 输出 EPUB 路径（可选） |
| `-d`, `--directory` | 要批量处理的目录路径 |

---

## 注意事项

1. **备份**：转换会生成新文件，不会覆盖原文件；建议重要书籍先备份。
2. **编码**：内部按 UTF-8 处理 HTML，异常字符会忽略（`errors='ignore'`）。
3. **批量跳过规则**：文件名中已包含 `_simplified` 的 EPUB 会被跳过，避免重复转换。
4. **转换规则**：默认 `tw2s`，若需通用繁→简可在 `convert.py` 中把 `OpenCC('tw2s')` 改为 `OpenCC('t2s')`。

---

## 项目结构示例

```
.
├── convert.py      # 主脚本
├── README.md       # 本说明
└── 你的书.epub     # 待转换的 EPUB
```

运行后同目录下会生成 `你的书_simplified.epub`。

---

## 依赖说明

- **opencc-python-reimplemented**：繁简转换
- **EbookLib**：EPUB 读写与结构解析

---

## 许可与免责

仅供个人学习与正版书籍格式转换使用。请勿用于侵犯版权的电子书传播。

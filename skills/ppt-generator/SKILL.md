---
name: ppt-generator
description: PPT 幻灯片生成器（支持 Markdown/飞书文档转 PPT，5 大视觉排版，百度蓝配色）
homepage: https://github.com/openclaw/openclaw
license: Proprietary. See LICENSE.txt
metadata: {"openclaw": {"emoji": "📊", "requires": {"bins": ["python3"], "config": ["tools.exec.enabled", "tools.feishu-doc.enabled"]}, "primaryEnv": "PPT_TEMPLATE_PATH"}}
---

# PPT Generator Skill - PPT 幻灯片生成器

自动将 Markdown、飞书文档、会议纪要转换为专业的 PPT 幻灯片，支持 5 大视觉排版（总分/并列/流程/循环/金字塔），严格遵守百度蓝配色规范。

---

## ⚠️ 核心行为准则 (CRITICAL RULES)

1. **绝对禁止抢跑执行**：在收集完所有必要信息之前，**严禁**调用任何生成工具
2. **一步一问原则**：每次只询问一个关键参数，提问后**必须立即停止**，等待用户回答
3. **严格遵守排版基准**：生成的 PPT 必须使用规定的【配色方案】和【模板分析】数据

---

## 🎨 配色方案 (Office 主题)

| 颜色 | 十六进制 | RGB | 用途 |
|------|---------|-----|------|
| 深色 1 | `#000000` | 0,0,0 | 主要文字 |
| 浅色 1 | `#FFFFFF` | 255,255,255 | 背景 |
| 深色 2 | `#44546A` | 68,84,106 | 次要文字 |
| 浅色 2 | `#F2F2F2` | 242,242,242 | 浅灰底色 (卡片底色) |
| 强调色 1 | `#4472C4` | 68,114,196 | 蓝色强调（百度蓝，用于标题和边框） |
| 强调色 2 | `#ED7D31` | 237,125,49 | 橙色强调 (流程图箭头) |
| 强调色 3 | `#A5A5A5` | 165,165,165 | 灰色强调 |

---

## 📐 5 大动态排版基准

### 1. 【总分】(hierarchy)
- **布局**：顶部一段深蓝背景总结，下方并排多个详情卡片
- **适用**：核心观点 + 分点论述

### 2. 【并列】(parallel)
- **布局**：页面中均匀分布多个独立的图文卡片
- **适用**：多个平行要点

### 3. 【流程】(process)
- **布局**：卡片从左向右排列，中间带有橙色指向箭头
- **适用**：步骤、流程、时间线

### 4. 【循环】(cycle)
- **布局**：卡片呈环形闭环排列
- **适用**：闭环流程、周期性内容

### 5. 【金字塔】(pyramid)
- **布局**：卡片从下至上堆叠，显示层级关系
- **适用**：层级结构、重要性排序

---

## 🗣️ 对话状态机 (Workflow States)

### [State 1] 主题确认
- **AI 动作**：询问："我们在制作 PPT。请告诉我 PPT 的【主题标题】是什么？"
- **限制**：🛑 **在此强制停顿，等待用户输入。**

### [State 2] 内容来源确认
- **AI 动作**：询问："好的。请问 PPT 内容来源是？
  1. Markdown 文本
  2. 飞书文档（请提供链接）
  3. 我来帮你生成大纲"
- **限制**：🛑 **在此强制停顿，等待用户输入。**

### [State 3] 内容收集
- **AI 动作**：
  - 如果是 Markdown：直接使用
  - 如果是飞书文档：调用 `feishu_doc.read` 读取内容
  - 如果需要生成大纲：询问行业和主题，生成结构化大纲
- **限制**：🛑 **在此强制停顿，等待用户确认内容。**

### [State 4] 排版选择（核心交互）
- **AI 动作**：询问："接下来请选择 PPT 的排版风格：
  1. 【总分】- 顶部总结 + 下方详情
  2. 【并列】- 均匀分布多个卡片
  3. 【流程】- 从左到右带箭头
  4. 【循环】- 环形闭环排列
  5. 【金字塔】- 从下至上堆叠
  
  或者让我根据内容自动分配版式？"
- **限制**：🛑 **在此强制停顿，等待用户选择。**

### [State 5] 主题风格确认
- **AI 动作**：询问："最后，请选择 PPT 的配色风格：
  1. 商务深蓝（百度蓝，推荐）
  2. 科技蓝黑
  3. 简约黑白灰"
- **限制**：🛑 **在此强制停顿，等待用户选择。**

### [State 6] 生成与输出
- **AI 动作**：
  1. 整合所有收集的信息
  2. 生成 `presentation_data.json`
  3. 调用 `generate.py` 生成 PPT
  4. 输出文件路径并提供下载链接
- **限制**：✅ **此时可以执行生成命令**

---

## 💡 使用示例

```
用户：把这篇文档转成 PPT
https://my.feishu.cn/docx/xxx

AI：我们在制作 PPT。请告诉我 PPT 的【主题标题】是什么？

用户：季度报告

AI：好的。请问 PPT 内容来源是？
1. Markdown 文本
2. 飞书文档（请提供链接）
3. 我来帮你生成大纲

用户：飞书文档

AI：好的，正在读取飞书文档...
（调用 feishu_doc.read 读取内容）

AI：文档已读取。接下来请选择 PPT 的排版风格：
1. 【总分】- 顶部总结 + 下方详情
2. 【并列】- 均匀分布多个卡片
3. 【流程】- 从左到右带箭头
4. 【循环】- 环形闭环排列
5. 【金字塔】- 从下至上堆叠

用户：流程

AI：最后，请选择 PPT 的配色风格：
1. 商务深蓝（百度蓝，推荐）
2. 科技蓝黑
3. 简约黑白灰

用户：商务深蓝

AI：好的，正在生成 PPT...
（调用 generate.py 生成）

AI：✅ PPT 已生成！
文件路径：/path/to/output.pptx
```

---

## 🔧 技术实现

### 依赖安装

```bash
# 安装 python-pptx
pip install python-pptx

# 验证安装
python -c "from pptx import Presentation; print('OK')"
```

### 脚本结构

```
skills/ppt-generator/
├── SKILL.md                  # 本配置文件
├── generate.py               # PPT 生成引擎（支持 5 大排版）
├── templates/                # PPT 模板文件
│   ├── business.pptx         # 商务深蓝模板
│   ├── tech.pptx             # 科技蓝黑模板
│   └── simple.pptx           # 简约黑白模板
└── scripts/
    ├── parse_markdown.py     # Markdown 解析
    ├── feishu_reader.py      # 飞书文档读取
    └── layout_engine.py      # 排版引擎
```

### JSON 数据契约

```json
{
  "title": "PPT 标题",
  "theme": "business/tech/simple",
  "slides": [
    {
      "type": "cover/content/summary",
      "title": "幻灯片标题",
      "layout": "hierarchy/parallel/process/pyramid/cycle",
      "summary": "可选的顶部总结",
      "items": [
        {"title": "小标题 1", "content": "详细描述 1"},
        {"title": "小标题 2", "content": "详细描述 2"}
      ]
    }
  ]
}
```

---

## ⚠️ 限制说明

| 功能 | 支持情况 | 说明 |
|------|---------|------|
| 文字内容 | ✅ 完全支持 | 标题、列表、段落 |
| 5 大排版 | ✅ 完全支持 | 总分/并列/流程/循环/金字塔 |
| 百度蓝配色 | ✅ 完全支持 | 严格遵守官方配色 |
| 图片插入 | ⚠️ 部分支持 | 需要手动添加 |
| 图表生成 | ❌ 不支持 | 需手动添加 |
| 动画效果 | ❌ 不支持 | PPT 生成后手动添加 |
| 飞书文档读取 | ✅ 完全支持 | 需要飞书 API 权限 |

---

## 📋 配置示例

在 `openclaw.json` 中添加：

```json
{
  "skills": {
    "entries": {
      "ppt-generator": {
        "enabled": true,
        "config": {
          "defaultTheme": "business",
          "defaultLayout": "auto",
          "outputFormat": "pptx",
          "autoUpload": true
        }
      }
    }
  }
}
```

---

## 🔗 相关资源

- **Skill 位置**：`workspace/skills/ppt-generator/`
- **python-pptx 文档**：https://python-pptx.readthedocs.io/
- **飞书开放平台**：https://open.feishu.cn/
- **ClawHub**：https://clawhub.com

---

*版本：2.0.0（参考百度智能云 Skill 格式）*
*创建日期：2026-03-08*
*作者：OpenClaw*

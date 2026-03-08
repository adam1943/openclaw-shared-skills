# TOOLS.md - Local Notes

## Feishu 应用管理

### Skills 发现库（定期更新）

**OpenClaw Skills 发现库多维表格**
- 链接：https://my.feishu.cn/base/RmrNb1JWkaAAXSsFwj3cCw1rnYc
- app_token: `RmrNb1JWkaAAXSsFwj3cCw1rnYc`
- table_id: `tblSgJEBxk04aMb1`

**字段结构：**
| 字段名 | 类型 | 说明 |
|--------|------|------|
| Skill 名称 | 文本 | 主字段 |
| 分类 | 单选 | 文档写作/PPT 生成/股票交易/数据分析/自动化/AI 工具/其他 |
| 描述 | 文本 | 功能说明 |
| 来源链接 | URL | ClawHub/GitHub 等 |
| 安装命令 | 文本 | clawhub install 命令 |
| 所需权限 | 文本 | API Key/权限码 |
| 推荐指数 | 单选 | ⭐⭐⭐⭐⭐ ~ ⭐ |
| 发现日期 | 日期时间 | 自动记录 |
| 状态 | 单选 | 已安装/待测试/已验证/不推荐 |

**重点关注领域：**
- 📄 文档写作（PPT 生成、Markdown、PDF）
- 📊 股票交易（量化、行情、交易 API）
- 🤖 自动化工具
- 🧠 AI 工具集成

**更新频率：** 每周自动搜索并更新

---

## Feishu 文档管理

### 多维表格文档管理（推荐）

**OpenClaw 文档管理多维表格**
- 链接：https://my.feishu.cn/base/FFxybIfLua8OPMs92qSccdwEnRe
- app_token: `FFxybIfLua8OPMs92qSccdwEnRe`
- table_id: `tblcIAsyOBIFFaCG`

**字段结构：**
| 字段名 | 类型 | 说明 |
|--------|------|------|
| 文档名称 | 文本 | 主字段 |
| 文档链接 | URL | 飞书文档链接 |
| 分类 | 单选 | OpenClaw / 技术文档 / 笔记 / 项目 |
| 创建时间 | 日期时间 | 自动记录 |

**工作流程：**
1. 创建文档 → `feishu_doc.create`
2. 登记到表格 → `feishu_bitable_create_record`
3. 后续可通过表格筛选和管理

### 文件夹结构
- **openclaw 文件夹**: `F6JGf20J7lN9aed7vVac9bU8nlg`
- 完整链接：https://my.feishu.cn/drive/folder/F6JGf20J7lN9aed7vVac9bU8nlg
- 状态：⚠️ 个人云盘 API 访问受限，暂时手动移动

### 权限状态
- ✅ `space:document:move` - 移动云空间文件夹和云文档
- ✅ `space:document:retrieve` - 获取云空间文件夹下的云文档清单
- ✅ `drive:file` - 文件操作
- ✅ `drive:drive` - 云空间管理
- ✅ `bitable:app` - 多维表格操作

---

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.

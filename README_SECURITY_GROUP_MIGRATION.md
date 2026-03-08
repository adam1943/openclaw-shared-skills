# 火山引擎 → 百度云 安全组迁移工具

## 功能说明

本工具用于将火山引擎 (Volcengine) 的安全组配置导出并迁移到百度云 (Baidu Cloud)。

### 支持的功能

- ✅ 导出火山引擎所有安全组及规则
- ✅ 自动转换规则格式（端口、协议、CIDR 等）
- ✅ 批量导入到百度云 VPC
- ✅ 导出备份为 JSON 文件
- ✅ 详细的迁移报告

---

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置密钥

**方式一：环境变量**

```bash
# 火山引擎
export VOLC_ACCESS_KEY="your_volc_access_key"
export VOLC_SECRET_KEY="your_volc_secret_key"
export VOLC_REGION="cn-beijing"
export VOLC_VPC_ID=""  # 可选，指定 VPC

# 百度云
export BAIDU_ACCESS_KEY="your_baidu_access_key"
export BAIDU_SECRET_KEY="your_baidu_secret_key"
export BAIDU_REGION="bj"
```

**方式二：配置文件**

创建 `config.json` 文件：

```json
{
  "volc_access_key": "your_volc_access_key",
  "volc_secret_key": "your_volc_secret_key",
  "volc_region": "cn-beijing",
  "volc_vpc_id": "",
  "baidu_access_key": "your_baidu_access_key",
  "baidu_secret_key": "your_baidu_secret_key",
  "baidu_region": "bj"
}
```

### 3. 获取 API 密钥

#### 火山引擎
1. 登录 [火山引擎控制台](https://console.volcengine.com/)
2. 进入「访问控制」→「密钥管理」
3. 创建或获取 Access Key

#### 百度云
1. 登录 [百度智能云控制台](https://console.bce.baidu.com/)
2. 进入「安全认证」→「Access Key」
3. 创建或获取 Access Key

### 4. 运行迁移

```bash
python security_group_migration.py
```

---

## 配置参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `volc_access_key` | 火山引擎 Access Key | 必填 |
| `volc_secret_key` | 火山引擎 Secret Key | 必填 |
| `volc_region` | 火山引擎区域 | `cn-beijing` |
| `volc_vpc_id` | 指定 VPC（可选） | 空（所有 VPC） |
| `baidu_access_key` | 百度云 Access Key | 必填 |
| `baidu_secret_key` | 百度云 Secret Key | 必填 |
| `baidu_region` | 百度云区域 | `bj` |

### 区域代码参考

**火山引擎区域：**
- `cn-beijing` - 北京
- `cn-shanghai` - 上海
- `cn-guangzhou` - 广州

**百度云区域：**
- `bj` - 北京
- `su` - 苏州
- `gz` - 广州

---

## 规则转换说明

工具会自动转换以下字段：

| 字段 | 火山引擎 | 百度云 |
|------|----------|--------|
| 方向 | ingress/egress | ingress/egress |
| 协议 | tcp/udp/icmp | tcp/udp/icmp |
| 端口范围 | 80/80 | 80/80 |
| 策略 | accept/drop | allow/deny |
| 源 CIDR | SourceCidrIp | source_cidr |
| 目标 CIDR | DestCidrIp | dest_cidr |

---

## 输出示例

```
============================================================
火山引擎 -> 百度云 安全组迁移工具
============================================================
开始导出火山引擎安全组...
找到 3 个安全组
  ✓ 导出：web-sg (5 条规则)
  ✓ 导出：db-sg (3 条规则)
  ✓ 导出：admin-sg (2 条规则)

✓ 导出已保存到：security_groups_export.json

============================================================
开始导入 3 个安全组到百度云
============================================================

导入安全组：web-sg
  描述：Web 服务器安全组
  规则数：5
  ✓ 创建安全组：web-sg -> sg-abc123
    ✓ 添加规则：tcp 80/80
    ✓ 添加规则：tcp 443/443
    ...
  成功导入 5/5 条规则

============================================================
迁移完成!
============================================================
总计：3 个安全组
成功：3 个
失败：0 个
```

---

## 注意事项

⚠️ **使用前请仔细阅读**

1. **权限要求**：确保 API 密钥具有 VPC 和安全组的读写权限
2. **VPC 映射**：目标百度云需要预先创建对应的 VPC
3. **规则限制**：百度云安全组规则数量有限制（默认 50 条/组）
4. **频率限制**：工具内置了 API 调用间隔，避免触发限流
5. **备份**：导出会自动保存为 JSON 文件，建议先备份再导入

---

## 故障排查

### 问题：认证失败
**解决**：检查 Access Key 和 Secret Key 是否正确，确认密钥未过期

### 问题：区域错误
**解决**：确认区域代码正确，火山引擎使用 `cn-xxx`，百度云使用短代码

### 问题：VPC 不存在
**解决**：在百度云控制台预先创建对应的 VPC

### 问题：规则导入失败
**解决**：检查规则是否超出百度云限制，查看具体错误信息

---

## 扩展开发

如需自定义规则转换逻辑，可修改以下类：

- `VolcengineSecurityGroupExporter` - 火山引擎导出逻辑
- `BaiduCloudSecurityGroupImporter` - 百度云导入逻辑
- `SecurityGroupRule` - 规则数据模型

---

## 许可证

MIT License

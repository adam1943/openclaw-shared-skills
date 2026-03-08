#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
火山引擎安全组迁移到百度云工具
Security Group Migration Tool: Volcengine to Baidu Cloud

功能:
1. 从火山引擎导出安全组配置
2. 将安全组规则转换并导入到百度云

依赖:
pip install volcengine bce-python-sdk

使用前请配置:
- VOLC_ACCESS_KEY / VOLC_SECRET_KEY
- BAIDU_ACCESS_KEY / BAIDU_SECRET_KEY
- 区域配置
"""

import json
import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict

# 火山引擎 SDK
from volcengine.vpc import VpcService
from volcengine.util import Util

# 百度云 SDK
from baidubce.auth import bce_credentials
from baidubce.http import bce_http_client
from baidubce.services.vpc import vpc_client


@dataclass
class SecurityGroupRule:
    """安全组规则数据模型"""
    direction: str  # ingress/egress
    protocol: str   # tcp/udp/icmp
    port_range: str  # 端口范围，如 "80/80" 或 "1/65535"
    source_cidr: Optional[str] = None  # 源 CIDR (入方向)
    dest_cidr: Optional[str] = None    # 目标 CIDR (出方向)
    policy: str = "accept"  # accept/drop
    priority: int = 1
    description: str = ""


@dataclass
class SecurityGroup:
    """安全组数据模型"""
    name: str
    description: str
    vpc_id: str
    rules: List[SecurityGroupRule]


class VolcengineSecurityGroupExporter:
    """火山引擎安全组导出器"""
    
    def __init__(self, access_key: str, secret_key: str, region: str = "cn-beijing"):
        self.access_key = access_key
        self.secret_key = secret_key
        self.region = region
        
        # 初始化火山引擎 VPC 服务
        self.vpc_service = VpcService()
        self.vpc_service.set_host(f"vpc.{region}.volces.com")
        self.vpc_service.set_credentials(access_key, secret_key)
    
    def describe_security_groups(self, vpc_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """获取所有安全组列表"""
        params = {
            "MaxResults": 100,
        }
        if vpc_id:
            params["VpcId"] = vpc_id
        
        try:
            response = self.vpc_service.describe_security_groups(params)
            return response.get("SecurityGroups", [])
        except Exception as e:
            print(f"获取安全组列表失败：{e}")
            return []
    
    def describe_security_group_rules(self, security_group_id: str) -> List[Dict[str, Any]]:
        """获取安全组规则详情"""
        params = {
            "SecurityGroupId": security_group_id,
            "MaxResults": 100,
        }
        
        try:
            response = self.vpc_service.describe_security_group_rules(params)
            return response.get("SecurityGroupRules", [])
        except Exception as e:
            print(f"获取安全组规则失败 {security_group_id}: {e}")
            return []
    
    def export_security_group(self, sg_info: Dict[str, Any]) -> SecurityGroup:
        """导出单个安全组及其规则"""
        sg_id = sg_info.get("SecurityGroupId")
        sg_name = sg_info.get("SecurityGroupName", sg_id)
        sg_desc = sg_info.get("Description", "")
        vpc_id = sg_info.get("VpcId", "")
        
        # 获取规则
        rules_raw = self.describe_security_group_rules(sg_id)
        rules = []
        
        for rule in rules_raw:
            direction = rule.get("Direction", "ingress")
            protocol = rule.get("IpProtocol", "tcp").lower()
            port_range = rule.get("PortRange", "1/65535")
            policy = "accept" if rule.get("Policy", "accept") == "accept" else "drop"
            priority = rule.get("Priority", 1)
            
            # 处理 CIDR
            if direction == "ingress":
                source_cidr = rule.get("SourceCidrIp", "0.0.0.0/0")
                dest_cidr = None
            else:
                source_cidr = None
                dest_cidr = rule.get("DestCidrIp", "0.0.0.0/0")
            
            rules.append(SecurityGroupRule(
                direction=direction,
                protocol=protocol,
                port_range=port_range,
                source_cidr=source_cidr,
                dest_cidr=dest_cidr,
                policy=policy,
                priority=priority,
                description=rule.get("Description", "")
            ))
        
        return SecurityGroup(
            name=sg_name,
            description=sg_desc,
            vpc_id=vpc_id,
            rules=rules
        )
    
    def export_all(self, vpc_id: Optional[str] = None) -> List[SecurityGroup]:
        """导出所有安全组"""
        print(f"开始导出火山引擎安全组...")
        
        sg_list = self.describe_security_groups(vpc_id)
        print(f"找到 {len(sg_list)} 个安全组")
        
        security_groups = []
        for sg_info in sg_list:
            sg = self.export_security_group(sg_info)
            security_groups.append(sg)
            print(f"  ✓ 导出：{sg.name} ({len(sg.rules)} 条规则)")
        
        return security_groups


class BaiduCloudSecurityGroupImporter:
    """百度云安全组导入器"""
    
    def __init__(self, access_key: str, secret_key: str, region: str = "bj"):
        self.access_key = access_key
        self.secret_key = secret_key
        self.region = region
        
        # 初始化百度云 VPC 客户端
        self.client = vpc_client.VpcClient(
            bce_credentials.BceCredentials(access_key, secret_key),
            f"https://vpc.{region}.baidubce.com"
        )
    
    def create_security_group(self, sg: SecurityGroup) -> Optional[str]:
        """创建安全组"""
        try:
            # 百度云创建安全组
            response = self.client.create_security_group(
                name=sg.name,
                description=sg.description,
                vpc_id=sg.vpc_id
            )
            
            sg_id = response.security_group_id
            print(f"  ✓ 创建安全组：{sg.name} -> {sg_id}")
            return sg_id
            
        except Exception as e:
            print(f"  ✗ 创建安全组失败 {sg.name}: {e}")
            return None
    
    def add_security_group_rule(self, sg_id: str, rule: SecurityGroupRule) -> bool:
        """添加安全组规则"""
        try:
            # 转换规则为百度云格式
            direction = "ingress" if rule.direction == "ingress" else "egress"
            
            # 百度云规则参数
            rule_params = {
                "direction": direction,
                "protocol": rule.protocol,
                "port_range": rule.port_range,
                "policy": "allow" if rule.policy == "accept" else "deny",
                "priority": rule.priority,
                "description": rule.description or "",
            }
            
            # 设置 CIDR
            if direction == "ingress" and rule.source_cidr:
                rule_params["source_cidr"] = rule.source_cidr
            elif direction == "egress" and rule.dest_cidr:
                rule_params["dest_cidr"] = rule.dest_cidr
            else:
                rule_params["source_cidr"] = "0.0.0.0/0"
            
            # 添加规则
            self.client.authorize_security_group_rule(
                security_group_id=sg_id,
                **rule_params
            )
            
            return True
            
        except Exception as e:
            print(f"    ✗ 添加规则失败：{rule.protocol} {rule.port_range} - {e}")
            return False
    
    def import_security_group(self, sg: SecurityGroup) -> bool:
        """导入单个安全组"""
        print(f"\n导入安全组：{sg.name}")
        print(f"  描述：{sg.description}")
        print(f"  规则数：{len(sg.rules)}")
        
        # 创建安全组
        sg_id = self.create_security_group(sg)
        if not sg_id:
            return False
        
        # 添加规则
        success_count = 0
        for rule in sg.rules:
            if self.add_security_group_rule(sg_id, rule):
                success_count += 1
            time.sleep(0.1)  # 避免频率限制
        
        print(f"  成功导入 {success_count}/{len(sg.rules)} 条规则")
        return success_count > 0
    
    def import_all(self, security_groups: List[SecurityGroup]) -> Dict[str, Any]:
        """批量导入安全组"""
        print(f"\n{'='*60}")
        print(f"开始导入 {len(security_groups)} 个安全组到百度云")
        print(f"{'='*60}")
        
        results = {
            "total": len(security_groups),
            "success": 0,
            "failed": 0,
            "details": []
        }
        
        for sg in security_groups:
            success = self.import_security_group(sg)
            if success:
                results["success"] += 1
                results["details"].append({"name": sg.name, "status": "success"})
            else:
                results["failed"] += 1
                results["details"].append({"name": sg.name, "status": "failed"})
            
            time.sleep(0.5)  # 避免 API 频率限制
        
        return results


def load_config_from_env() -> Dict[str, str]:
    """从环境变量加载配置"""
    import os
    
    config = {
        "volc_access_key": os.getenv("VOLC_ACCESS_KEY", ""),
        "volc_secret_key": os.getenv("VOLC_SECRET_KEY", ""),
        "volc_region": os.getenv("VOLC_REGION", "cn-beijing"),
        "volc_vpc_id": os.getenv("VOLC_VPC_ID", ""),  # 可选，指定 VPC
        
        "baidu_access_key": os.getenv("BAIDU_ACCESS_KEY", ""),
        "baidu_secret_key": os.getenv("BAIDU_SECRET_KEY", ""),
        "baidu_region": os.getenv("BAIDU_REGION", "bj"),
    }
    
    return config


def validate_config(config: Dict[str, str]) -> bool:
    """验证配置是否完整"""
    required = [
        "volc_access_key", "volc_secret_key",
        "baidu_access_key", "baidu_secret_key"
    ]
    
    missing = [k for k in required if not config.get(k)]
    
    if missing:
        print("❌ 缺少以下配置:")
        for key in missing:
            print(f"   - {key}")
        print("\n请设置环境变量或编辑 config.json")
        return False
    
    return True


def save_export_to_file(security_groups: List[SecurityGroup], filename: str = "security_groups_export.json"):
    """将导出的安全组保存到文件"""
    data = []
    for sg in security_groups:
        data.append({
            "name": sg.name,
            "description": sg.description,
            "vpc_id": sg.vpc_id,
            "rules": [asdict(rule) for rule in sg.rules]
        })
    
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ 导出已保存到：{filename}")


def main():
    """主函数"""
    print("="*60)
    print("火山引擎 -> 百度云 安全组迁移工具")
    print("="*60)
    
    # 加载配置
    config = load_config_from_env()
    
    # 尝试从 config.json 加载配置
    try:
        with open("config.json", "r", encoding="utf-8") as f:
            file_config = json.load(f)
            config.update(file_config)
    except FileNotFoundError:
        pass
    
    # 验证配置
    if not validate_config(config):
        print("\n配置示例 (config.json):")
        print(json.dumps({
            "volc_access_key": "your_volc_access_key",
            "volc_secret_key": "your_volc_secret_key",
            "volc_region": "cn-beijing",
            "volc_vpc_id": "",  # 可选
            "baidu_access_key": "your_baidu_access_key",
            "baidu_secret_key": "your_baidu_secret_key",
            "baidu_region": "bj"
        }, indent=2))
        return
    
    # 导出火山引擎安全组
    exporter = VolcengineSecurityGroupExporter(
        config["volc_access_key"],
        config["volc_secret_key"],
        config.get("volc_region", "cn-beijing")
    )
    
    vpc_id = config.get("volc_vpc_id") or None
    security_groups = exporter.export_all(vpc_id)
    
    if not security_groups:
        print("\n⚠️  未找到任何安全组")
        return
    
    # 保存到文件（备份）
    save_export_to_file(security_groups)
    
    # 确认是否继续导入
    print(f"\n{'='*60}")
    confirm = input(f"是否将 {len(security_groups)} 个安全组导入到百度云？(y/n): ")
    if confirm.lower() != "y":
        print("已取消导入")
        return
    
    # 导入到百度云
    importer = BaiduCloudSecurityGroupImporter(
        config["baidu_access_key"],
        config["baidu_secret_key"],
        config.get("baidu_region", "bj")
    )
    
    results = importer.import_all(security_groups)
    
    # 输出结果
    print(f"\n{'='*60}")
    print("迁移完成!")
    print(f"{'='*60}")
    print(f"总计：{results['total']} 个安全组")
    print(f"成功：{results['success']} 个")
    print(f"失败：{results['failed']} 个")
    
    if results['failed'] > 0:
        print("\n失败的安全组:")
        for detail in results['details']:
            if detail['status'] == 'failed':
                print(f"  - {detail['name']}")


if __name__ == "__main__":
    main()

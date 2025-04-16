from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
import os
from dotenv import load_dotenv
import socket
import requests
from datetime import datetime, timedelta

class GoogleAdsService:
    """
    Google Ads API服务类
    """
    def __init__(self):
        """
        初始化Google Ads客户端（使用服务账号）
        """
        # 重新加载环境变量
        load_dotenv(override=True)
        
        # 设置经理账户ID和客户账户ID
        self.manager_customer_id = "8292857172"  # 经理账户ID
        self.customer_id = "8591579739"  # 客户账户ID
        print(f"经理账户ID: {self.manager_customer_id}")
        print(f"客户账户ID: {self.customer_id}")
            
        try:
            # 初始化客户端配置
            client_config = {
                "developer_token": os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN"),
                "use_proto_plus": True,
                "json_key_file_path": os.getenv("GOOGLE_ADS_JSON_KEY_PATH"),
                "login_customer_id": self.manager_customer_id  # 使用经理账户ID作为登录ID
            }
            
            # 设置代理（如果需要）
            proxy = os.getenv("HTTP_PROXY", "http://127.0.0.1:10809")
            os.environ["HTTP_PROXY"] = proxy  
            os.environ["HTTPS_PROXY"] = proxy
            print(f"设置环境代理: {proxy}")
            
            # 初始化客户端
            print("初始化Google Ads客户端...")
            self.client = GoogleAdsClient.load_from_dict(client_config)
            print("Google Ads 客户端初始化成功")
            
            # 验证可访问的客户账户
            self._validate_accessible_customers()
                
        except Exception as e:
            print(f"Google Ads 客户端初始化失败: {str(e)}")
            raise
            
    def _validate_accessible_customers(self):
        """验证和输出可访问的客户账户"""
        try:
            customer_service = self.client.get_service("CustomerService")
            resource_names = customer_service.list_accessible_customers()
            
            print(f"可访问的客户账户数量: {len(resource_names.resource_names)}")
            for resource_name in resource_names.resource_names:
                customer_id = resource_name.split('/')[-1]
                print(f"可访问的客户账户: {customer_id}")
                
            # 检查是否可以访问目标客户账户
            target_resource_name = f"customers/{self.customer_id}"
            if target_resource_name in resource_names.resource_names:
                print(f"✅ 可以直接访问目标客户账户: {self.customer_id}")
                self.can_access_customer = True
            else:
                print(f"❌ 无法直接访问目标客户账户: {self.customer_id}")
                print("需要通过经理账户间接访问客户账户")
                self.can_access_customer = False
                
        except Exception as e:
            print(f"验证客户账户访问权限失败: {str(e)}")
            self.can_access_customer = False
    
    def get_customer_clients(self):
        """
        获取经理账户下的客户客户端关系
        
        Returns:
            list: 客户账户列表
        """
        try:
            print(f"获取经理账户 {self.manager_customer_id} 下的客户账户...")
            
            # 获取CustomerClientLinkService
            client_service = self.client.get_service("CustomerClientLinkService")
            ga_service = self.client.get_service("GoogleAdsService")
            
            # 查询经理账户下的客户-客户端链接
            query = f"""
                SELECT
                  customer_client_link.client_customer,
                  customer_client_link.manager_link_id
                FROM customer_client_link
            """
            
            try:
                # 使用经理账户ID执行查询
                response = ga_service.search(
                    customer_id=self.manager_customer_id,
                    query=query
                )
                
                # 处理结果
                client_links = []
                for row in response:
                    client_customer = row.customer_client_link.client_customer
                    manager_link_id = row.customer_client_link.manager_link_id
                    client_id = client_customer.split('/')[-1]
                    
                    client_links.append({
                        'client_id': client_id,
                        'manager_link_id': manager_link_id
                    })
                    
                    # 特别检查是否找到了目标客户账户
                    if client_id == self.customer_id:
                        print(f"✅ 找到目标客户账户 {self.customer_id} 与经理账户的链接")
                
                print(f"找到 {len(client_links)} 个客户账户链接")
                return client_links
                
            except GoogleAdsException as ex:
                print(f"查询客户-客户端链接失败: {ex}")
                for error in ex.failure.errors:
                    print(f'\t错误消息: {error.message}')
                return []
                
        except Exception as e:
            print(f"获取客户账户链接失败: {str(e)}")
            return []
    
    def get_campaign_metrics(self, customer_id=None, start_date=None, end_date=None):
        """
        获取广告系列指标数据，考虑权限限制
        
        Args:
            customer_id (str, optional): 客户ID，如果不提供则使用默认客户ID
            start_date (str): 开始日期，格式：YYYY-MM-DD
            end_date (str): 结束日期，格式：YYYY-MM-DD
            
        Returns:
            list: 广告系列数据列表
        """
        try:
            # 如果未提供客户ID，则使用默认客户ID
            if not customer_id:
                customer_id = self.customer_id
                
            print(f"开始获取广告系列数据...")
            print(f"客户账户ID: {customer_id}")
            print(f"日期范围: {start_date} 至 {end_date}")
            
            # 构建查询
            ga_service = self.client.get_service("GoogleAdsService")
            
            # 首先获取所有广告系列基本信息，包括已删除的
            base_query = """
                SELECT
                    campaign.id,
                    campaign.name,
                    campaign.status
                FROM campaign
            """
            print(f"执行基础查询: {base_query}")
            
            try:
                base_response = ga_service.search(
                    customer_id=customer_id,
                    query=base_query
                )
                
                # 处理结果
                campaigns = []
                campaign_metrics = {}
                
                # 初始化所有广告系列的数据结构
                for row in base_response:
                    campaign_id = row.campaign.id
                    
                    # 获取和处理状态值
                    status = row.campaign.status
                    status_value = getattr(status, 'value', status)
                    print(f"状态详情 - 原始值: {status}, 值类型: {type(status)}, 提取值: {status_value}, 值类型: {type(status_value)}")
                    
                    # 更新广告状态映射（将数值2也映射为活跃状态）
                    status_name = self._get_status_name(status_value)
                    print(f"广告系列状态映射: {status_value} -> {status_name}")
                    
                    campaign_metrics[campaign_id] = {
                        'id': campaign_id,
                        'name': row.campaign.name,
                        'status': status_value,  # 保持原始值
                        'status_name': status_name,  # 添加解释名称
                        'impressions': 0,
                        'clicks': 0,
                        'cost': 0,
                        'conversions': 0
                    }
                    print(f"找到广告系列: {row.campaign.name} (ID: {campaign_id}), 状态: {status_value} ({status_name})")
                
                # 如果没有找到任何广告系列，返回空列表
                if not campaign_metrics:
                    print("未找到任何广告系列")
                    return []
                
                # 获取指定日期范围内的指标数据
                metrics_query = f"""
                    SELECT
                        campaign.id,
                        campaign.name,
                        campaign.status,
                        segments.date,
                        metrics.impressions,
                        metrics.clicks,
                        metrics.cost_micros,
                        metrics.conversions
                    FROM campaign
                    WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
                """
                print(f"执行指标查询: {metrics_query}")
                
                metrics_response = ga_service.search(
                    customer_id=customer_id,
                    query=metrics_query
                )
                
                # 汇总每个广告系列的指标
                for row in metrics_response:
                    campaign_id = row.campaign.id
                    if campaign_id in campaign_metrics:
                        metrics = campaign_metrics[campaign_id]
                        metrics['impressions'] += row.metrics.impressions
                        metrics['clicks'] += row.metrics.clicks
                        metrics['cost'] += row.metrics.cost_micros / 1000000
                        metrics['conversions'] += row.metrics.conversions
                        print(f"更新广告系列 {row.campaign.name} 的指标数据 (日期: {row.segments.date}):")
                        print(f"- 展示: +{row.metrics.impressions}")
                        print(f"- 点击: +{row.metrics.clicks}")
                        print(f"- 花费: +${row.metrics.cost_micros / 1000000:.2f}")
                        print(f"- 转化: +{row.metrics.conversions}")
                
                # 计算每个广告系列的衍生指标并添加到结果列表
                for campaign in campaign_metrics.values():
                    campaign['ctr'] = (campaign['clicks'] / campaign['impressions'] * 100) if campaign['impressions'] > 0 else 0
                    campaign['cpc'] = (campaign['cost'] / campaign['clicks']) if campaign['clicks'] > 0 else 0
                    campaigns.append(campaign)
                    print(f"\n广告系列汇总数据 - {campaign['name']}:")
                    print(f"- 状态: {campaign['status']} ({campaign['status_name']})")
                    print(f"- 总展示: {campaign['impressions']}")
                    print(f"- 总点击: {campaign['clicks']}")
                    print(f"- 总花费: ${campaign['cost']:.2f}")
                    print(f"- 总转化: {campaign['conversions']}")
                    print(f"- 点击率: {campaign['ctr']:.2f}%")
                    print(f"- CPC: ${campaign['cpc']:.2f}")
                
                print(f"\n✅ 成功获取并汇总 {len(campaigns)} 个广告系列数据")
                return campaigns
                
            except GoogleAdsException as ex:
                print(f"❌ 查询失败: {ex}")
                print("错误详情:")
                for error in ex.failure.errors:
                    print(f"\t- {error.message}")
                    if hasattr(error, 'error_code'):
                        print(f"\t- 错误代码: {error.error_code}")
                    if hasattr(error, 'trigger') and error.trigger:
                        print(f"\t- 错误触发器: {error.trigger.string_value}")
                # 异常情况下返回空列表
                return []
                    
        except Exception as e:
            print(f"❌ 获取广告系列数据时发生未知错误: {str(e)}")
            import traceback
            print("错误堆栈:")
            print(traceback.format_exc())
            # 异常情况下返回空列表
            return []

    def get_customer_accounts(self):
        """
        获取经理账户下的所有客户账户
        
        Returns:
            list: 客户账户列表
        """
        try:
            # 使用经理账户ID进行查询
            print(f"尝试使用经理账户ID: {self.manager_customer_id} 获取关联的客户账户")
            
            # 获取客户链接服务
            customer_service = self.client.get_service("CustomerService")
            print("成功获取 Customer 服务")
            
            # 获取accessible_customers
            print("获取可访问的客户账户列表...")
            resource_names = customer_service.list_accessible_customers()
            print(f"找到 {len(resource_names.resource_names)} 个可访问的客户账户")
            
            # 获取每个客户的详细信息
            accounts = []
            for resource_name in resource_names.resource_names:
                customer_id = resource_name.split('/')[-1]
                print(f"找到客户账户: {customer_id}")
                
                # 检查是否是我们要查找的客户账户
                if customer_id == self.customer_id:
                    print(f"找到目标客户账户: {customer_id}")
                    
                    # 尝试获取更多信息
                    try:
                        print(f"获取客户账户 {customer_id} 的详细信息...")
                        ga_service = self.client.get_service("GoogleAdsService")
                        
                        # 使用经理账户ID查询特定客户账户信息
                        query = f"""
                            SELECT
                                customer_client.id,
                                customer_client.descriptive_name,
                                customer_client.currency_code,
                                customer_client.time_zone,
                                customer_client.status
                            FROM customer_client
                            WHERE customer_client.id = {customer_id}
                        """
                        
                        response = ga_service.search(
                            customer_id=self.manager_customer_id,
                            query=query
                        )
                        
                        for row in response:
                            account = {
                                'id': row.customer_client.id,
                                'name': row.customer_client.descriptive_name,
                                'currency': row.customer_client.currency_code,
                                'time_zone': row.customer_client.time_zone,
                                'status': row.customer_client.status
                            }
                            accounts.append(account)
                            print(f"成功获取客户账户 {customer_id} 的详细信息")
                    except Exception as e:
                        print(f"获取客户账户 {customer_id} 详细信息失败: {str(e)}")
                        # 如果获取详细信息失败，至少添加基本信息
                        accounts.append({
                            'id': customer_id,
                            'name': '未知'
                        })
            
            # 如果没有找到目标客户账户，也获取一下所有客户账户
            if not accounts:
                print("未找到目标客户账户，尝试获取所有关联的客户账户...")
                
                # 使用经理账户ID查询客户账户
                ga_service = self.client.get_service("GoogleAdsService")
                query = """
                    SELECT
                        customer_client.id,
                        customer_client.descriptive_name,
                        customer_client.currency_code,
                        customer_client.time_zone,
                        customer_client.status,
                        customer_client.manager
                    FROM customer_client
                    WHERE customer_client.status = 'ENABLED'
                """
                
                response = ga_service.search(
                    customer_id=self.manager_customer_id,
                    query=query
                )
                
                for row in response:
                    account = {
                        'id': row.customer_client.id,
                        'name': row.customer_client.descriptive_name,
                        'currency': row.customer_client.currency_code,
                        'time_zone': row.customer_client.time_zone,
                        'status': row.customer_client.status,
                        'manager': row.customer_client.manager
                    }
                    accounts.append(account)
            
            print(f"成功获取 {len(accounts)} 个客户账户")
            return accounts
            
        except GoogleAdsException as ex:
            print(f'Google Ads API 请求失败，错误信息：{ex}')
            for error in ex.failure.errors:
                print(f'\t错误类型: {error.error_code.enum_value}')
                print(f'\t错误消息: {error.message}')
            return []
        except Exception as e:
            print(f'发生未知错误：{str(e)}')
            return [] 

    def get_daily_metrics(self, start_date=None, end_date=None):
        """
        获取每日指标数据用于图表展示
        
        Args:
            start_date (str): 开始日期，格式：YYYY-MM-DD
            end_date (str): 结束日期，格式：YYYY-MM-DD
            
        Returns:
            list: 每日指标数据列表
        """
        try:
            print(f"开始获取每日指标数据，日期范围: {start_date} 至 {end_date}")
            ga_service = self.client.get_service("GoogleAdsService")
            
            query = f"""
                SELECT
                    segments.date,
                    metrics.impressions,
                    metrics.clicks,
                    metrics.cost_micros,
                    metrics.conversions
                FROM campaign
                WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
                ORDER BY segments.date ASC
            """
            print(f"每日指标查询: {query}")
            
            try:
                print(f"执行查询，客户ID: {self.customer_id}")
                response = ga_service.search(
                    customer_id=self.customer_id,
                    query=query
                )
                
                # 初始化结果字典，确保每一天都有数据
                start = datetime.strptime(start_date, '%Y-%m-%d')
                end = datetime.strptime(end_date, '%Y-%m-%d')
                date_range = (end - start).days + 1
                print(f"初始化日期范围: {date_range}天")
                
                daily_metrics = {
                    (start + timedelta(days=x)).strftime('%Y-%m-%d'): {
                        'date': (start + timedelta(days=x)).strftime('%Y-%m-%d'),
                        'impressions': 0,
                        'clicks': 0,
                        'cost': 0,
                        'conversions': 0
                    }
                    for x in range(date_range)
                }
                
                # 填充实际数据
                row_count = 0
                for row in response:
                    row_count += 1
                    date = row.segments.date
                    daily_metrics[date].update({
                        'impressions': row.metrics.impressions,
                        'clicks': row.metrics.clicks,
                        'cost': row.metrics.cost_micros / 1000000,
                        'conversions': row.metrics.conversions
                    })
                    print(f"日期 {date} - 展示: {row.metrics.impressions}, 点击: {row.metrics.clicks}, 花费: ${row.metrics.cost_micros / 1000000:.2f}")
                
                print(f"API返回了 {row_count} 行数据")
                
                # 转换为列表并按日期排序
                result = list(daily_metrics.values())
                result.sort(key=lambda x: x['date'])
                
                print(f"准备返回 {len(result)} 天的数据")
                return result
                
            except GoogleAdsException as ex:
                print(f"❌ 获取每日指标数据查询失败: {ex}")
                print("错误详情:")
                for error in ex.failure.errors:
                    print(f"\t- {error.message}")
                    if hasattr(error, 'error_code'):
                        print(f"\t- 错误代码: {error.error_code}")
                    if hasattr(error, 'trigger') and error.trigger:
                        print(f"\t- 错误触发器: {error.trigger.string_value}")
                return []
                
        except Exception as e:
            print(f"❌ 获取每日指标数据时发生未知错误: {str(e)}")
            import traceback
            print("错误堆栈:")
            print(traceback.format_exc())
            return [] 

    def _get_status_name(self, status_value):
        """
        将Google Ads API的状态值映射为可读的状态名称
        """
        try:
            # 尝试将状态值转换为整数，以便于映射
            status_int = int(float(status_value))
            status_map = {
                1: "活跃",  # ENABLED
                2: "活跃",  # PAUSED，根据用户反馈，这个状态实际上是活跃的
                3: "已删除"  # REMOVED
            }
            return status_map.get(status_int, f"{status_value} (未知)")
        except (ValueError, TypeError):
            # 如果无法转换为整数，返回原值
            if status_value == "ENABLED":
                return "活跃"
            elif status_value == "PAUSED":
                return "活跃"  # 根据用户反馈，PAUSED状态也是活跃的
            elif status_value == "REMOVED":
                return "已删除"
            else:
                return f"{status_value} (未知)"
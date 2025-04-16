from app.services.google_ads_service import GoogleAdsService
from datetime import datetime, timedelta

def test_google_ads_api():
    """
    综合测试Google Ads API功能
    """
    try:
        # 初始化服务
        service = GoogleAdsService()
        print("\n=== 初始化测试完成 ===")
        
        # 设置日期范围（最近7天）
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        # 格式化日期
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')
        
        print(f"\n=== 测试日期范围: {start_date_str} 至 {end_date_str} ===")
        
        # 测试1: 获取客户-客户端链接关系
        print("\n=== 测试1: 获取客户-客户端链接关系 ===")
        client_links = service.get_customer_clients()
        
        if client_links:
            print("\n找到的客户-客户端链接:")
            for link in client_links:
                print(f"客户ID: {link['client_id']}, 链接ID: {link['manager_link_id']}")
        
        # 测试2: 尝试获取客户账户的广告系列数据
        print("\n=== 测试2: 获取客户账户广告系列数据 ===")
        campaigns = service.get_campaign_metrics(
            customer_id=service.customer_id,  # 使用客户账户ID
            start_date=start_date_str,
            end_date=end_date_str
        )
        
        if campaigns:
            print("\n获取到的广告系列数据:")
            for campaign in campaigns:
                print(f"\n广告系列ID: {campaign['id']}")
                print(f"广告系列名称: {campaign['name']}")
                print(f"展示次数: {campaign['impressions']}")
                print(f"点击次数: {campaign['clicks']}")
                print(f"花费: {campaign['cost']}")
        else:
            print("\n无法获取客户账户广告系列数据")
            
        # 测试3: 尝试获取经理账户的客户列表
        print("\n=== 测试3: 获取经理账户下的所有客户账户 ===")
        # 使用CustomerService.list_accessible_customers
        try:
            customer_service = service.client.get_service("CustomerService")
            response = customer_service.list_accessible_customers()
            print(f"可访问的客户账户数量: {len(response.resource_names)}")
            
            # 显示所有可访问的客户账户
            for resource_name in response.resource_names:
                customer_id = resource_name.split('/')[-1]
                print(f"客户账户ID: {customer_id}")
        except Exception as e:
            print(f"获取可访问客户账户失败: {e}")
        
        # 总结
        print("\n=== 测试总结 ===")
        print("1. 服务账号是否可以连接到Google Ads API?", "是" if service.client else "否")
        print("2. 服务账号是否可以访问经理账户?", "是" if client_links is not None else "否")
        print("3. 服务账号是否可以直接访问客户账户?", "是" if service.can_access_customer else "否")
        print("4. 客户账户是否与经理账户有链接关系?", "是" if any(link['client_id'] == service.customer_id for link in client_links) else "否")
        print("5. 是否能获取客户账户广告系列数据?", "是" if campaigns else "否")
        
        print("\n如果有任何'否'的项目，请参考以下建议:")
        print("1. 确保服务账号已被添加到经理账户，并具有足够权限")
        print("2. 确保经理账户和客户账户之间存在链接关系")
        print("3. 考虑直接将服务账号添加到客户账户")
        print("4. 检查Google Ads界面中的账户权限设置")
        
    except Exception as e:
        print(f"测试过程中发生错误: {str(e)}")

if __name__ == "__main__":
    test_google_ads_api() 
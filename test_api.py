from app.services.google_ads_service import GoogleAdsService
from datetime import datetime, timedelta

def test_api():
    """
    测试Google Ads API调用
    """
    try:
        # 初始化服务
        service = GoogleAdsService()
        print("服务初始化成功")
        
        # 设置日期范围（最近7天）
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        # 格式化日期
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')
        
        print(f"\n开始日期: {start_date_str}")
        print(f"结束日期: {end_date_str}")
        
        try:
            # 获取数据
            campaigns = service.get_campaign_metrics(
                customer_id="8591579739",  # 使用实际的客户账户ID
                start_date=start_date_str,
                end_date=end_date_str
            )
            
            if not campaigns:
                print("没有找到广告系列数据")
                return
                
            print("\n获取到的广告系列数据:")
            for campaign in campaigns:
                print(f"\n广告系列名称: {campaign['name']}")
                print(f"展示次数: {campaign['impressions']}")
                print(f"点击次数: {campaign['clicks']}")
                print(f"花费: {campaign['cost']}")
                print(f"转化次数: {campaign['conversions']}")
                print(f"转化价值: {campaign['conversions_value']}")
                
        except Exception as e:
            print(f"获取广告系列数据失败: {str(e)}")
            
    except Exception as e:
        print(f"测试失败: {str(e)}")

if __name__ == "__main__":
    test_api() 
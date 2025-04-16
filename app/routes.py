from flask import Blueprint, render_template, jsonify, request
from app.services.google_ads_service import GoogleAdsService
from datetime import datetime, timedelta
import os

bp = Blueprint('dashboard', __name__)
ads_service = GoogleAdsService()

@bp.route('/')
def index():
    """渲染仪表板页面"""
    return render_template('dashboard.html')

@bp.route('/api/metrics')
def get_metrics():
    """获取广告指标数据"""
    try:
        # 获取日期范围
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if not start_date or not end_date:
            # 默认获取最近7天的数据，避免数据量太大
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            
        print(f"获取指标数据: {start_date} 至 {end_date}")
        
        # 获取广告系列数据
        print("调用get_campaign_metrics获取广告系列数据...")
        campaigns = ads_service.get_campaign_metrics(
            start_date=start_date,
            end_date=end_date
        )
        
        if not campaigns:
            print("没有获取到广告系列数据，返回空结果")
            return jsonify({
                'total_cost': 0,
                'total_clicks': 0,
                'total_impressions': 0,
                'ctr': 0,
                'cpc': 0,
                'begin_checkout': 0,
                'daily_metrics': []
            })
        
        # 计算汇总指标
        print(f"计算汇总指标，广告系列数量: {len(campaigns)}")
        total_cost = sum(c['cost'] for c in campaigns)
        total_clicks = sum(c['clicks'] for c in campaigns)
        total_impressions = sum(c['impressions'] for c in campaigns)
        total_conversions = sum(c['conversions'] for c in campaigns)
        
        # 计算衍生指标
        ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
        cpc = (total_cost / total_clicks) if total_clicks > 0 else 0
        
        print(f"计算结果:")
        print(f"- 总花费: ${total_cost:.2f}")
        print(f"- 总点击: {total_clicks}")
        print(f"- 总展示: {total_impressions}")
        print(f"- 点击率: {ctr:.2f}%")
        print(f"- CPC: ${cpc:.2f}")
        print(f"- 发起结账数: {total_conversions}")
        
        # 获取每日指标数据用于图表
        print("调用get_daily_metrics获取每日数据...")
        daily_metrics = ads_service.get_daily_metrics(
            start_date=start_date,
            end_date=end_date
        )
        print(f"获取到 {len(daily_metrics)} 天的每日数据")
        
        # 计算每日发起结账总数
        daily_checkout_total = sum(day.get('begin_checkout', 0) for day in daily_metrics)
        print(f"从每日数据中汇总的发起结账总数: {daily_checkout_total}")
        
        result = {
            'total_cost': round(total_cost, 2),
            'total_clicks': total_clicks,
            'total_impressions': total_impressions,
            'ctr': round(ctr, 2),
            'cpc': round(cpc, 2),
            'begin_checkout': daily_checkout_total,  # 使用从每日数据中汇总的发起结账数
            'daily_metrics': daily_metrics
        }
        print("准备返回数据:", result)
        
        return jsonify(result)
        
    except Exception as e:
        print(f"获取指标数据时发生错误: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@bp.route('/api/campaigns')
def get_campaigns():
    """获取活跃广告系列数据"""
    try:
        # 获取日期范围
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if not start_date or not end_date:
            # 默认获取最近7天的数据
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            
        print(f"获取广告系列数据: {start_date} 至 {end_date}")
        
        # 获取广告系列数据
        print("调用get_campaign_metrics获取广告系列数据...")
        campaigns = ads_service.get_campaign_metrics(
            start_date=start_date,
            end_date=end_date
        )
        
        # 输出原始数据
        print(f"原始广告系列数据: {len(campaigns)} 条")
        for i, campaign in enumerate(campaigns):
            # 记录状态值的详细信息，但不添加到返回数据中
            status = campaign['status']
            status_type = type(status).__name__
            print(f"广告系列 {i+1}: {campaign['name']} (ID: {campaign['id']}) - 状态: {status}, 类型: {status_type}")
        
        # 处理所有广告系列数据
        all_campaigns = campaigns
            
        # 按展示量降序排序
        all_campaigns.sort(key=lambda x: x['impressions'], reverse=True)
        
        print(f"返回所有广告系列: {len(all_campaigns)} 条")
        return jsonify(all_campaigns)
        
    except Exception as e:
        print(f"获取广告系列数据时发生错误: {str(e)}")
        import traceback
        print(traceback.format_exc())
        
        # 如果发生错误，仍然尝试返回一个空列表
        return jsonify([])

@bp.route('/api/ad_groups/<campaign_id>')
def get_ad_groups(campaign_id):
    """获取特定广告系列下的广告组数据"""
    try:
        # 获取日期范围
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if not start_date or not end_date:
            # 默认获取最近7天的数据
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            
        print(f"获取广告系列 {campaign_id} 的广告组数据: {start_date} 至 {end_date}")
        
        # 获取广告组数据
        ad_groups = ads_service.get_ad_group_metrics(
            campaign_id=campaign_id,
            start_date=start_date,
            end_date=end_date
        )
        
        print(f"为广告系列 {campaign_id} 返回 {len(ad_groups)} 个广告组数据")
        return jsonify(ad_groups)
        
    except Exception as e:
        print(f"获取广告组数据时发生错误: {str(e)}")
        import traceback
        print(traceback.format_exc())
        
        # 如果发生错误，返回空列表
        return jsonify([]) 
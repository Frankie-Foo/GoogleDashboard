from flask import Flask
from dotenv import load_dotenv
import os

def create_app():
    """创建Flask应用实例"""
    # 加载环境变量
    load_dotenv()
    
    # 创建应用实例
    app = Flask(__name__)
    
    # 注册蓝图
    from .routes import bp as dashboard_bp
    app.register_blueprint(dashboard_bp)
    
    return app 
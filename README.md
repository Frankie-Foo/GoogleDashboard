# Google Ads Dashboard

一个用于展示和分析Google广告数据的仪表板应用。

## 功能特点

- 展示广告账户总览数据
- 显示花费与转化趋势
- 展示点击和展示趋势
- 支持多种时间范围筛选
- 活跃广告系列详情展示

## 技术栈

- 后端：Python Flask
- 前端：HTML, JavaScript, Tailwind CSS
- 图表：Chart.js
- API：Google Ads API

## 安装步骤

1. 克隆仓库
```bash
git clone [repository-url]
cd [repository-name]
```

2. 创建并激活虚拟环境
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. 安装依赖
```bash
pip install -r requirements.txt
```

4. 配置环境变量
创建 `.env` 文件并添加以下配置：
```
GOOGLE_ADS_DEVELOPER_TOKEN=your_developer_token
GOOGLE_ADS_CLIENT_ID=your_client_id
GOOGLE_ADS_CLIENT_SECRET=your_client_secret
GOOGLE_ADS_REFRESH_TOKEN=your_refresh_token
GOOGLE_ADS_LOGIN_CUSTOMER_ID=your_customer_id
GOOGLE_ADS_JSON_KEY_PATH=path_to_your_service_account_key.json
```

5. 运行应用
```bash
python run.py
```

## 使用说明

1. 访问 `http://localhost:5000` 打开仪表板
2. 使用顶部的时间筛选按钮选择不同的时间范围
3. 查看账户总览数据和趋势图表
4. 查看活跃广告系列的详细数据

## 开发说明

- `app/` - 应用主目录
  - `templates/` - HTML模板文件
  - `static/` - 静态资源文件
  - `services/` - 业务逻辑服务
  - `routes.py` - 路由定义
  - `__init__.py` - 应用初始化

## 注意事项

- 确保已经获取了Google Ads API的访问权限
- 正确配置了服务账号和相关凭据
- 环境变量中的客户ID必须是有效的10位数字 
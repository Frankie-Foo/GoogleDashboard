// 初始化图表
let costConversionChart = null;
let clicksImpressionsChart = null;

// 当前视图状态
let isShowingCampaigns = false;

// 当前日期范围
let currentDateRange = {
    startDate: null,
    endDate: null
};

// 初始化日期选择器
let dateRangePicker = null;

// 显示加载状态
function showLoading(id, isLoading = true) {
    const element = document.getElementById(id);
    if (element) {
        element.innerHTML = isLoading ? '加载中...' : '--';
    }
}

// 显示错误状态
function showError(id, message = '加载失败') {
    const element = document.getElementById(id);
    if (element) {
        element.innerHTML = message;
        element.classList.add('text-red-500');
    }
}

// 更新数据卡片
function updateMetrics(startDate, endDate) {
    // 显示所有指标为加载中状态
    showLoading('total-cost');
    showLoading('total-clicks');
    showLoading('total-impressions');
    showLoading('ctr');
    showLoading('cpc');
    showLoading('begin_checkout');
    
    console.log(`正在获取指标数据: ${startDate} 至 ${endDate}`);
    
    const params = new URLSearchParams({
        start_date: startDate,
        end_date: endDate
    });

    fetch(`/api/metrics?${params}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`API请求失败: ${response.status} ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('获取到指标数据:', data);
            
            if (data.error) {
                console.error('API返回错误:', data.error);
                showError('total-cost', '获取失败');
                showError('total-clicks', '获取失败');
                showError('total-impressions', '获取失败');
                showError('ctr', '获取失败');
                showError('cpc', '获取失败');
                showError('begin_checkout', '获取失败');
                return;
            }

            // 更新数据卡片
            document.getElementById('total-cost').textContent = data.total_cost.toLocaleString();
            document.getElementById('total-clicks').textContent = data.total_clicks.toLocaleString();
            document.getElementById('total-impressions').textContent = data.total_impressions.toLocaleString();
            document.getElementById('ctr').textContent = data.ctr.toFixed(2);
            document.getElementById('cpc').textContent = data.cpc.toFixed(2);
            document.getElementById('begin_checkout').textContent = data.begin_checkout.toLocaleString();

            // 更新图表
            updateCharts(data.daily_metrics);
        })
        .catch(error => {
            console.error('获取指标数据失败:', error);
            // 显示错误状态
            showError('total-cost', '获取失败');
            showError('total-clicks', '获取失败');
            showError('total-impressions', '获取失败');
            showError('ctr', '获取失败');
            showError('cpc', '获取失败');
            showError('begin_checkout', '获取失败');
        });
}

// 获取状态文本
function getStatusText(status) {
    // 转换为字符串以便于比较
    status = String(status);
    
    // 谷歌广告API返回的状态值可能是数字、枚举值或字符串
    if (status === 'ENABLED' || status === '2' || status === '2.0') {
        return '活跃';
    } else if (status === 'PAUSED' || status === '3' || status === '3.0') {
        return '暂停';
    } else if (status === 'REMOVED' || status === '4' || status === '4.0') {
        return '已删除';
    } else {
        // 打印未知状态进行调试
        console.log('未知广告状态值:', status);
        return status;
    }
}

// 判断广告系列是否活跃
function isActive(status) {
    // 转换为字符串以便于比较
    status = String(status);
    return status === 'ENABLED' || status === '2' || status === '2.0';
}

// 更新广告系列详情
function updateCampaignDetails(startDate, endDate) {
    console.log(`正在获取广告系列数据: ${startDate} 至 ${endDate}`);
    
    // 显示加载中状态
    const tableBody = document.getElementById('campaignTableBody');
    tableBody.innerHTML = `<tr class="text-center"><td colspan="8" class="py-8 text-gray-400">加载中...</td></tr>`;
    
    const params = new URLSearchParams({
        start_date: startDate,
        end_date: endDate
    });

    fetch(`/api/campaigns?${params}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`API请求失败: ${response.status} ${response.statusText}`);
            }
            return response.json();
        })
        .then(campaigns => {
            console.log(`获取到 ${campaigns.length} 个广告系列数据`);
            tableBody.innerHTML = '';

            // 过滤出活跃的广告系列
            const activeCampaigns = campaigns.filter(campaign => isActive(campaign.status));
            console.log(`活跃广告系列: ${activeCampaigns.length} 个`);

            if (activeCampaigns.length === 0) {
                const row = document.createElement('tr');
                row.className = 'text-center';
                row.innerHTML = `<td colspan="8" class="py-8 text-gray-400">暂无活跃广告系列数据</td>`;
                tableBody.appendChild(row);
                return;
            }

            activeCampaigns.forEach(campaign => {
                // 创建广告系列行
                const campaignRow = document.createElement('tr');
                campaignRow.className = 'border-b border-gray-700 campaign-row';
                campaignRow.dataset.campaignId = campaign.id;
                
                // 获取状态文本
                const statusText = getStatusText(campaign.status);
                
                campaignRow.innerHTML = `
                    <td class="py-3 px-4">
                        <div class="flex items-center">
                            <button class="mr-2 text-blue-400 expand-btn" data-campaign-id="${campaign.id}">
                                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                    <polyline points="9 18 15 12 9 6"></polyline>
                                </svg>
                            </button>
                            ${campaign.name}
                        </div>
                    </td>
                    <td class="text-right py-3 px-4 text-green-500">
                        ${statusText}
                    </td>
                    <td class="text-right py-3 px-4">${campaign.cost.toLocaleString()}</td>
                    <td class="text-right py-3 px-4">${campaign.clicks.toLocaleString()}</td>
                    <td class="text-right py-3 px-4">${campaign.impressions.toLocaleString()}</td>
                    <td class="text-right py-3 px-4">${campaign.ctr.toFixed(2)}</td>
                    <td class="text-right py-3 px-4">${campaign.cpc.toFixed(2)}</td>
                    <td class="text-right py-3 px-4">${campaign.begin_checkout.toLocaleString()}</td>
                `;
                tableBody.appendChild(campaignRow);
                
                // 创建广告组行容器（初始隐藏）
                const adGroupsContainer = document.createElement('tr');
                adGroupsContainer.className = 'ad-groups-container hidden';
                adGroupsContainer.dataset.campaignId = campaign.id;
                adGroupsContainer.innerHTML = `
                    <td colspan="8" class="p-0">
                        <div class="ad-groups-table-container bg-gray-900 pl-8 pr-4 py-3">
                            <h4 class="text-sm text-blue-300 mb-2">广告组详情</h4>
                            <div class="ad-groups-loading text-center py-4 text-gray-400">点击展开按钮加载广告组数据...</div>
                            <table class="min-w-full ad-groups-table hidden">
                                <thead>
                                    <tr class="border-b border-gray-700">
                                        <th class="text-left py-2 px-2 text-xs">广告组名称</th>
                                        <th class="text-right py-2 px-2 text-xs">状态</th>
                                        <th class="text-right py-2 px-2 text-xs">花费 ($)</th>
                                        <th class="text-right py-2 px-2 text-xs">点击</th>
                                        <th class="text-right py-2 px-2 text-xs">展示</th>
                                        <th class="text-right py-2 px-2 text-xs">点击率 (%)</th>
                                        <th class="text-right py-2 px-2 text-xs">CPC ($)</th>
                                        <th class="text-right py-2 px-2 text-xs">发起结账数</th>
                                    </tr>
                                </thead>
                                <tbody class="ad-groups-tbody"></tbody>
                            </table>
                        </div>
                    </td>
                `;
                tableBody.appendChild(adGroupsContainer);
            });
            
            // 添加展开/收起事件监听器
            document.querySelectorAll('.expand-btn').forEach(button => {
                button.addEventListener('click', function(e) {
                    e.preventDefault();
                    const campaignId = this.dataset.campaignId;
                    const campaignRow = document.querySelector(`.campaign-row[data-campaign-id="${campaignId}"]`);
                    const adGroupsContainer = document.querySelector(`.ad-groups-container[data-campaign-id="${campaignId}"]`);
                    
                    // 切换广告组容器的显示状态
                    adGroupsContainer.classList.toggle('hidden');
                    
                    // 切换展开按钮的图标
                    if (adGroupsContainer.classList.contains('hidden')) {
                        // 收起状态 - 显示向右箭头
                        this.innerHTML = `
                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <polyline points="9 18 15 12 9 6"></polyline>
                            </svg>
                        `;
                    } else {
                        // 展开状态 - 显示向下箭头
                        this.innerHTML = `
                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <polyline points="6 9 12 15 18 9"></polyline>
                            </svg>
                        `;
                        
                        // 加载广告组数据
                        loadAdGroupsData(campaignId, startDate, endDate, adGroupsContainer);
                    }
                });
            });
        })
        .catch(error => {
            console.error('获取广告系列数据失败:', error);
            tableBody.innerHTML = `<tr class="text-center"><td colspan="8" class="py-8 text-red-500">加载数据失败，请刷新页面重试 (${error.message})</td></tr>`;
        });
}

// 加载广告组数据
function loadAdGroupsData(campaignId, startDate, endDate, container) {
    const loadingElem = container.querySelector('.ad-groups-loading');
    const tableElem = container.querySelector('.ad-groups-table');
    const tbodyElem = container.querySelector('.ad-groups-tbody');
    
    // 显示加载中状态
    loadingElem.textContent = '加载中...';
    loadingElem.classList.remove('hidden');
    tableElem.classList.add('hidden');
    
    const params = new URLSearchParams({
        start_date: startDate,
        end_date: endDate
    });
    
    fetch(`/api/ad_groups/${campaignId}?${params}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`API请求失败: ${response.status} ${response.statusText}`);
            }
            return response.json();
        })
        .then(adGroups => {
            console.log(`获取到广告系列 ${campaignId} 的 ${adGroups.length} 个广告组数据`);
            
            if (adGroups.length === 0) {
                loadingElem.textContent = '该广告系列下没有广告组数据';
                return;
            }
            
            // 隐藏加载中提示，显示表格
            loadingElem.classList.add('hidden');
            tableElem.classList.remove('hidden');
            
            // 清空表格内容
            tbodyElem.innerHTML = '';
            
            // 填充广告组数据
            adGroups.forEach(adGroup => {
                const row = document.createElement('tr');
                row.className = 'border-b border-gray-800';
                
                const statusText = getStatusText(adGroup.status);
                
                row.innerHTML = `
                    <td class="py-2 px-2 text-sm">${adGroup.name}</td>
                    <td class="text-right py-2 px-2 text-sm text-green-500">${statusText}</td>
                    <td class="text-right py-2 px-2 text-sm">${adGroup.cost.toLocaleString()}</td>
                    <td class="text-right py-2 px-2 text-sm">${adGroup.clicks.toLocaleString()}</td>
                    <td class="text-right py-2 px-2 text-sm">${adGroup.impressions.toLocaleString()}</td>
                    <td class="text-right py-2 px-2 text-sm">${adGroup.ctr.toFixed(2)}</td>
                    <td class="text-right py-2 px-2 text-sm">${adGroup.cpc.toFixed(2)}</td>
                    <td class="text-right py-2 px-2 text-sm">${adGroup.begin_checkout.toLocaleString()}</td>
                `;
                
                tbodyElem.appendChild(row);
            });
        })
        .catch(error => {
            console.error(`获取广告组数据失败:`, error);
            loadingElem.textContent = `加载失败: ${error.message}`;
            loadingElem.classList.add('text-red-500');
        });
}

// 初始化图表
function initCharts() {
    try {
        console.log('初始化图表...');
        // 花费与发起结账趋势图表（组合图表：花费用柱状图，发起结账用折线图）
        const costConversionCtx = document.getElementById('cost-conversion-chart').getContext('2d');
        costConversionChart = new Chart(costConversionCtx, {
            type: 'bar', // 基础类型为柱状图
            data: {
                labels: [],
                datasets: [
                    {
                        label: '花费',
                        backgroundColor: 'rgba(76, 175, 80, 0.5)',
                        borderColor: '#4CAF50',
                        borderWidth: 1,
                        data: [],
                        order: 1
                    },
                    {
                        label: '发起结账数',
                        type: 'line', // 显式设置为折线图类型
                        borderColor: '#2196F3',
                        backgroundColor: 'rgba(33, 150, 243, 0.1)',
                        borderWidth: 2,
                        pointRadius: 3,
                        pointBackgroundColor: '#2196F3',
                        fill: false,
                        tension: 0.4, // 添加弧度使线条更平滑
                        data: [],
                        order: 0, // 使折线显示在柱状图上方
                        yAxisID: 'y1' // 使用第二个Y轴
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                        labels: {
                            usePointStyle: true,
                            boxWidth: 10
                        }
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false
                    }
                },
                scales: {
                    x: {
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        },
                        ticks: {
                            color: 'rgba(255, 255, 255, 0.7)'
                        }
                    },
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: '花费 ($)',
                            color: 'rgba(255, 255, 255, 0.7)'
                        },
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        },
                        ticks: {
                            color: 'rgba(255, 255, 255, 0.7)'
                        }
                    },
                    y1: {
                        beginAtZero: true,
                        position: 'right',
                        title: {
                            display: true,
                            text: '发起结账数量',
                            color: 'rgba(255, 255, 255, 0.7)'
                        },
                        grid: {
                            drawOnChartArea: false // 不显示第二个Y轴的网格线
                        },
                        ticks: {
                            color: 'rgba(255, 255, 255, 0.7)'
                        }
                    }
                }
            }
        });

        // 点击和展示趋势图表（面积图与折线图组合）
        const clicksImpressionsCtx = document.getElementById('clicks-impressions-chart').getContext('2d');
        clicksImpressionsChart = new Chart(clicksImpressionsCtx, {
            type: 'line', // 基础类型为折线图
            data: {
                labels: [],
                datasets: [
                    {
                        label: '点击',
                        backgroundColor: 'rgba(255, 193, 7, 0.2)',
                        borderColor: '#FFC107',
                        borderWidth: 2,
                        pointRadius: 3,
                        pointBackgroundColor: '#FFC107',
                        tension: 0.4,
                        fill: true, // 填充区域，形成面积图效果
                        data: [],
                        order: 1
                    },
                    {
                        label: '展示',
                        backgroundColor: 'rgba(156, 39, 176, 0.1)',
                        borderColor: '#9C27B0',
                        borderWidth: 2,
                        pointRadius: 3,
                        pointBackgroundColor: '#9C27B0',
                        tension: 0.4,
                        fill: false, // 不填充
                        data: [],
                        order: 0,
                        yAxisID: 'y1' // 使用第二个Y轴
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                        labels: {
                            usePointStyle: true,
                            boxWidth: 10
                        }
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false
                    }
                },
                scales: {
                    x: {
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        },
                        ticks: {
                            color: 'rgba(255, 255, 255, 0.7)'
                        }
                    },
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: '点击数',
                            color: 'rgba(255, 255, 255, 0.7)'
                        },
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        },
                        ticks: {
                            color: 'rgba(255, 255, 255, 0.7)'
                        }
                    },
                    y1: {
                        beginAtZero: true,
                        position: 'right',
                        title: {
                            display: true,
                            text: '展示数',
                            color: 'rgba(255, 255, 255, 0.7)'
                        },
                        grid: {
                            drawOnChartArea: false // 不显示第二个Y轴的网格线
                        },
                        ticks: {
                            color: 'rgba(255, 255, 255, 0.7)'
                        }
                    }
                }
            }
        });
        console.log('图表初始化成功');
    } catch (error) {
        console.error('图表初始化失败:', error);
    }
}

// 更新图表数据
function updateCharts(dailyMetrics) {
    try {
        console.log(`更新图表数据，共 ${dailyMetrics.length} 天`);
        const labels = dailyMetrics.map(d => d.date);
        
        costConversionChart.data.labels = labels;
        costConversionChart.data.datasets[0].data = dailyMetrics.map(d => d.cost);
        costConversionChart.data.datasets[1].data = dailyMetrics.map(d => d.begin_checkout || d.conversions);
        costConversionChart.update();

        clicksImpressionsChart.data.labels = labels;
        clicksImpressionsChart.data.datasets[0].data = dailyMetrics.map(d => d.clicks);
        clicksImpressionsChart.data.datasets[1].data = dailyMetrics.map(d => d.impressions);
        clicksImpressionsChart.update();
        console.log('图表更新成功');
    } catch (error) {
        console.error('更新图表失败:', error);
    }
}

// 设置日期范围
function setDateRange(days) {
    console.log(`设置日期范围: ${days}`);
    const now = new Date(); // 当前日期
    let startDate, endDate;

    if (days === 'prev-month') {
        // 上月：从上月第一天到上月最后一天
        startDate = new Date(now.getFullYear(), now.getMonth() - 1, 1);
        endDate = new Date(now.getFullYear(), now.getMonth(), 0); // 上月最后一天
    } else if (days === 'this-month') {
        // 本月：从本月第一天到今天
        startDate = new Date(now.getFullYear(), now.getMonth(), 1);
        endDate = new Date(now);
    } else if (days === 1) {
        // 昨日：昨天的00:00到昨天的23:59
        endDate = new Date(now);
        endDate.setDate(endDate.getDate() - 1);
        startDate = new Date(endDate); // 复制昨天的日期
    } else if (days === 'prev-day') {
        // 前日：前天的00:00到前天的23:59
        const twoDaysAgo = new Date(now);
        twoDaysAgo.setDate(twoDaysAgo.getDate() - 2);
        startDate = new Date(twoDaysAgo);
        endDate = new Date(twoDaysAgo);
        console.log(`前日日期设置为: ${formatDate(startDate)}`);
    } else {
        // 最近n天：从n天前到昨天
        endDate = new Date(now);
        endDate.setDate(endDate.getDate() - 1); // 截止到昨天
        startDate = new Date(now);
        startDate.setDate(startDate.getDate() - days);
    }

    // 更新日期选择器的值
    dateRangePicker.setDate([startDate, endDate]);

    // 更新当前日期范围
    currentDateRange.startDate = formatDate(startDate);
    currentDateRange.endDate = formatDate(endDate);

    console.log(`日期范围设置为: ${currentDateRange.startDate} 至 ${currentDateRange.endDate}`);
    refreshData();
}

// 格式化日期为YYYY-MM-DD
function formatDate(date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
}

// 刷新数据
function refreshData() {
    console.log('开始刷新数据...');
    // 同时加载账户总览和广告系列详情
    updateMetrics(currentDateRange.startDate, currentDateRange.endDate);
    updateCampaignDetails(currentDateRange.startDate, currentDateRange.endDate);
}

// 切换视图
function toggleView() {
    const accountOverview = document.getElementById('accountOverview');
    const campaignDetails = document.getElementById('campaignDetails');
    const viewCampaignsBtn = document.getElementById('viewCampaigns');

    isShowingCampaigns = !isShowingCampaigns;

    if (isShowingCampaigns) {
        accountOverview.classList.add('hidden');
        campaignDetails.classList.remove('hidden');
        viewCampaignsBtn.textContent = '返回账户总览';
        updateCampaignDetails(currentDateRange.startDate, currentDateRange.endDate);
    } else {
        accountOverview.classList.remove('hidden');
        campaignDetails.classList.add('hidden');
        viewCampaignsBtn.textContent = '查看广告系列详情';
        updateMetrics(currentDateRange.startDate, currentDateRange.endDate);
    }
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    console.log('页面加载完成，开始初始化...');
    
    // 初始化日期选择器
    dateRangePicker = flatpickr("#dateRange", {
        mode: "range",
        locale: "zh",
        dateFormat: "Y-m-d",
        defaultDate: [new Date().setDate(new Date().getDate() - 30), new Date().setDate(new Date().getDate() - 1)],
        maxDate: "today",
        theme: "dark",
        onChange: function(selectedDates) {
            if (selectedDates.length === 2) {
                currentDateRange.startDate = formatDate(selectedDates[0]);
                currentDateRange.endDate = formatDate(selectedDates[1]);
            }
        }
    });
    
    // 初始化图表
    initCharts();
    
    // 设置默认日期范围（最近30天）
    setDateRange(30);
    
    // 绑定时间筛选按钮事件
    document.querySelectorAll('.time-filter').forEach(button => {
        button.addEventListener('click', () => {
            setDateRange(button.dataset.days);
        });
    });
    
    // 绑定查询按钮事件
    document.querySelector('.search-button').addEventListener('click', () => {
        if (currentDateRange.startDate && currentDateRange.endDate) {
            console.log(`手动设置日期范围: ${currentDateRange.startDate} 至 ${currentDateRange.endDate}`);
            refreshData();
        } else {
            console.warn('请选择完整的日期范围');
        }
    });

    // 绑定视图切换按钮事件
    document.getElementById('viewCampaigns').addEventListener('click', toggleView);
}); 
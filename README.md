# 金融数据挖掘与量化投资实训平台技术文档
## 一、项目概述
　　这是一个综合性的金融数据分析平台，目的是通过 Python 技术栈构建一个交互式的金融分析平台。系统集成了数据清洗、财务评分、技术分析、机器学习预测及量化回测功能，支持用户通过 Web 界面进行全流程的金融数据分析实验。
## 二、技术架构
　　核心框架: Streamlit (Web 界面构建)  
　　数据处理: Pandas, NumPy  
　　可视化: Plotly (交互式图表), Matplotlib (静态图表)  
　　机器学习: Scikit-learn (分类模型、PCA、标准化)  
　　外部 API: 集成了 SiliconFlow 平台的 DeepSeek 大模型 API 进行智能投研分析  
　　数据存储: CSV, Excel  
## 三、核心功能模块
系统采用模块化设计，主要分为以下四大核心模块：  
### 3.1 市场总览与龙虎榜分析  
该模块提供**宏观市场行情**监控。  
**主要指数走势图:**  
　　1.功能: 绘制上证A股、深证A股（等权重平均计算）及沪深300指数的走势图。  
　　2.技术: 使用 plotly.subplots 创建 1x3 子图，展示指数随时间的变化。  
　　3.数据源: 合并后的复权交易数据、沪深300指数数据。  
**龙虎榜统计**:  
　　1.功能: 筛选指定时间段内累计涨跌幅超过 ±20% 的股票。  
　　2.算法: 结合价格计算法和日涨跌幅累乘法，通过差异校验确保数据准确性，并过滤异常交易日数据。  
　　3.输出: 展示涨幅榜和跌幅榜的股票代码、简称及交易所。  
<img width="1351" height="795" alt="image" src="https://github.com/user-attachments/assets/3276fc07-4682-4229-8de0-3f1c1e982ad3" />
### 3.2 行业与个股深度分析 
用户选择特定申万一级行业后，进入该行业的深度分析页面。  
**行业指数与个股走势**:  
　　展示该行业指数的走势图。  
　　展示行业内前6只股票的价格走势（2x3 子图）。  
<img width="1860" height="900" alt="image" src="https://github.com/user-attachments/assets/3f2d910d-4857-4522-be5d-f8a8a2723911" />

**数据详情页**:  
　　提供行业指数交易数据、上市公司基本信息、行业股票交易数据及财务数据的表格展示。  
**综合评价分析**:  
　　1.功能: 基于 PCA（主成分分析）对行业内的上市公司进行财务综合评分。  
　　2.流程:  
　　1）数据清洗: 处理空值和负值；  
　　2）标准化: 使用 StandardScaler；  
　　3）降维: 使用 PCA (累计贡献率 95%) 提取主成分；  
　　4）评分: 计算综合得分 F=∑(Y×λ)。  
　　3.可视化: 展示排名前 N 的股票及其得分柱状图。  
**收益率分析**:  
　　1.功能: 对综合评分排名前 N 的股票构建投资组合，计算持有期收益率，并与沪深300指数进行对比。  
　　2.输出: 显示个股收益率、组合平均收益率、超额收益 (Alpha) 及对比柱状图。  
### 3.3 技术指标与预测模型  
该模块专注于个股的价格趋势预测与量化策略构建。  
**技术指标计算:**   
　　1.支持指标: MA(5,10,20)、MACD (DIF, DEA, MACD)、KDJ (K, D, J)、RSI、OBV。  
　　2.实现: 通过滑动窗口和指数加权移动平均算法计算。  
<img width="1355" height="824" alt="image" src="https://github.com/user-attachments/assets/0114b0b9-2296-477f-a390-e0693a2deda2" />

**机器学习预测:**  
　　1.模型选择: 支持逻辑回归、随机森林、SVM、神经网络、梯度提升树。  
　　2.特征工程: 使用技术指标作为特征 (X)，以次日涨跌 (1/0) 作为标签 (y)。  
　　3.数据划分: 训练集(70%)、测试集(20%)、预测集(10%)。  
　　4.流程: 标准化 -> 模型训练 -> 预测 -> 准确率评估。  
<img width="1341" height="806" alt="image" src="https://github.com/user-attachments/assets/bd70d393-1eeb-4436-b8f6-82de9f5e84cc" />
<img width="1365" height="638" alt="image" src="https://github.com/user-attachments/assets/36166ad8-e6a5-43c3-b781-bc8928afcacf" />

**量化投资策略回测:**  
　　1.策略逻辑: 基于模型预测信号（1买入，0卖出）或简单趋势策略。  
　　2.回测指标: 计算策略资产曲线、买入持有曲线、胜率及总收益率。  
　　3.可视化: 绘制资产价值随时间变化的对比折线图。  
<img width="1860" height="895" alt="image" src="https://github.com/user-attachments/assets/9afe9cb1-e2a7-48a2-889c-507fa0b1af0d" />
<img width="1860" height="854" alt="image" src="https://github.com/user-attachments/assets/4ed110d7-be57-4f0d-a1ff-0adde4aa9cee" />

### 3.4 AI大模型 
　　1.功能: 调用 DeepSeek 大模型 API 生成专业的股票分析报告。  
　　2.集成: 使用 requests 库向 SiliconFlow 平台发送 POST 请求。  
　　3.Prompt 工程: 输入股票名称、代码、市盈率等基本信息，要求模型从基本面、技术面、行业地位等维度进行分析。  
<img width="1406" height="810" alt="image" src="https://github.com/user-attachments/assets/dd363b58-b9b5-48a2-b3f8-7ab25be591e5" />

## 四、关键代码逻辑解析  
### 4.1 综合评价函数 (Fr)  
```python
def Fr(data, year):
    # 数据筛选与清洗
    tdata = data[data['年度'] == year]
    data_x = tdata.iloc[:, 1:-1].dropna() # 去除无效列
    
    # PCA 分析
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    pca = PCA(n_components=0.95) # 保留95%信息
    Y = pca.fit_transform(X_scaled)
    
    # 综合得分计算
    gxl = pca.explained_variance_ratio_ # 贡献率
    F = (Y * gxl).sum(axis=1) # 加权求和
    return result_df
```
### 4.2 模型预测与回测  
代码中实现了从特征提取到模型预测的完整闭环，并特别处理了数据泄露问题（按时间顺序划分数据集，而非随机打乱）。  
### 4.3 DeepSeek API 调用  
```python
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}
data = {
    "model": "deepseek-ai/DeepSeek-OCR",
    "messages": [{"role": "user", "content": prompt}],
    "stream": False
}
response = requests.post(api_url, headers=headers, json=data)
```
## 五、注意事项
1. 数据准备: 将文档中提到的 CSV 和 Excel 文件（如 复权交易数据2023.csv, fin_data.csv 等）放置于项目根目录；  
2. AI 分析功能需要有效的 SiliconFlow API Key；  
3. 数据文件路径需与代码中的硬编码路径保持一致。  
## 六、总结
　　每个模块的代码都体现了相同的设计框架：在追求功能完整性的同时，始终保持代码的健壮性和可维护性。日志记录和调试信息的输出帮助开发者理解程序的运行状态。清晰的函数命名和详细的注释使得代码即使在没有文档的情况下也具有很好的可读性。这种编写方式不仅让当前项目更加可靠，也为后续的功能扩展和维护打下了良好基础。

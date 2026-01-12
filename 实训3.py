# shixun3.py
import pandas as pd
import os
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

def perform_financial_analysis(analysis_type="营业收入", level="新版一级行业", 
                              show_chart=True, selected_year=None):
    """
    执行申万行业财务分析
    参数:
        analysis_type: 分析类型，'营业收入' 或 '营业利润'
        level: 行业级别，'新版一级行业'、'新版二级行业'、'新版三级行业'
        show_chart: 是否显示图表
        selected_year: 选择的年份，如果为None则显示最新年份
    返回:
        df_sum: 汇总统计DataFrame
        fig: matplotlib图表对象（如果show_chart为True）
    """
    
    # 1. 合并不同年份数据到excel表
    path = "./" 
    data = []
    available_years = []
    
    # 遍历文件夹中的所有excel文件
    dir_files = os.listdir(path)
    for file_name in dir_files:
        # 筛选以"Data"开头，".xlsx"结尾的文件名
        if file_name.startswith("Data") and file_name.endswith(".xlsx"):
            # 构建完整路径
            file_path = os.path.join(path, file_name)
            try:
                # 读取Excel文件
                df = pd.read_excel(file_path, usecols=["ts_code", "营业收入", "营业利润"])
                # 从文件名提取年份
                year = file_name.replace("Data", "").replace(".xlsx", "")
                year_int = int(year)
                df["年份"] = year_int
                data.append(df)
                available_years.append(year_int)
            except Exception as e:
                st.warning(f"读取文件 {file_name} 时出错: {e}")
                continue
    
    if not data:
        st.error("未找到财务数据文件")
        return None, None, []
    
    # 合并所有数据
    merged_df = pd.concat(data, ignore_index=True)
    
    # 2. 关联申万行业分类表
    try:
        info = pd.read_excel('最新个股申万行业分类(完整版-截至7月末).xlsx')
        
        # 重命名列以确保一致性
        column_mapping = {
            '股票代码': '股票代码',
            'ts_code': '股票代码',
            '代码': '股票代码',
            '新版一级行业': '新版一级行业',
            '新版二级行业': '新版二级行业',
            '新版三级行业': '新版三级行业'
        }
        
        for old_col, new_col in column_mapping.items():
            if old_col in info.columns:
                info = info.rename(columns={old_col: new_col})
        
        # 合并数据
        merged_industry = pd.merge(
            merged_df, 
            info[["股票代码", "新版一级行业", "新版二级行业", "新版三级行业"]], 
            left_on="ts_code", 
            right_on="股票代码", 
            how="left"
        )
        
        # 移除没有行业分类的数据
        merged_industry = merged_industry.dropna(subset=[level])
        
    except FileNotFoundError:
        st.error("未找到行业分类文件: '最新个股申万行业分类(完整版-截至7月末).xlsx'")
        return None, None, []
    except Exception as e:
        st.error(f"关联行业分类时出错: {e}")
        return None, None, []
    
    # 3. 计算增长率
    merged_industry = merged_industry.sort_values(by=[level, "ts_code", "年份"])
    
    if analysis_type == "营业收入":
        # 计算营业收入增长率
        merged_industry["营业收入增长率"] = merged_industry.groupby([level, "ts_code"])["营业收入"].pct_change() * 100
        growth_col = "营业收入增长率"
        value_col = "营业收入"
    else:
        # 计算营业利润增长率
        merged_industry["营业利润增长率"] = merged_industry.groupby([level, "ts_code"])["营业利润"].pct_change() * 100
        growth_col = "营业利润增长率"
        value_col = "营业利润"
    
    # 填充缺失值
    merged_industry[growth_col] = merged_industry[growth_col].fillna(0)
    
    # 4. 行业汇总统计
    df_sum = merged_industry.groupby([level, "年份"]).agg(
        数值=(value_col, lambda x: x.astype(float).sum()),
        上市公司数量=("ts_code", "nunique")
    ).reset_index()
    
    # 按公式"(当前年份-上一年份)/上一年份"计算增长率
    df_sum = df_sum.sort_values([level, "年份"])
    df_sum["增长率"] = (df_sum["数值"] - df_sum.groupby(level)["数值"].shift(1)) / df_sum.groupby(level)["数值"].shift(1) * 100
    df_sum["增长率"] = df_sum["增长率"].fillna(0)
    
    # 重命名列
    df_sum = df_sum.rename(columns={
        level: "行业名称",
        "年份": "年度",
        "数值": analysis_type,
        "增长率": f"{analysis_type}增长率",
        "上市公司数量": "上市公司家数"
    })
    
    # 5. 获取可用年份列表
    available_years = sorted(set(available_years))
    
    # 6. 可视化：增长最快的8个行业柱状图（仅针对一级行业）
    fig = None
    if show_chart and level == "新版一级行业":
        # 确定要显示的年份
        if selected_year is None:
            # 如果没有指定年份，显示最新年份
            display_year = df_sum["年度"].max()
        else:
            display_year = selected_year
        
        # 筛选该年份的数据
        year_data = df_sum[df_sum["年度"] == display_year].copy()
        
        if not year_data.empty:
            # 获取增长率最高的8个行业
            top8 = year_data.nlargest(8, f"{analysis_type}增长率").sort_values(by=f"{analysis_type}增长率", ascending=False)
            
            # 创建柱状图 - 竖着的柱状图
            fig, ax = plt.subplots(figsize=(12, 6))
            
            # 设置中文字体
            plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
            plt.rcParams['axes.unicode_minus'] = False
            
            # 使用深紫色 (#4B0082) 
            bar_color = '#D8BFD8'
            
            # 创建竖着的柱状图
            bars = ax.bar(top8["行业名称"], top8[f"{analysis_type}增长率"], 
                         color=bar_color, edgecolor='white', linewidth=1.5)
            
            # 添加数值标签在柱子上方
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., 
                       height + (0.5 if height >= 0 else -2.5),
                       f'{height:.1f}%',
                       ha='center', va='bottom' if height >= 0 else 'top',
                       fontsize=9,
                       fontweight='bold',
                       color='black' if height >= 0 else 'red')
            
            # 设置图表样式
            ax.set_ylabel(f'{analysis_type}增长率（%）', fontsize=12)
            ax.set_xlabel('行业名称', fontsize=12)
            ax.set_title(f'{display_year}年 {analysis_type}增长率Top8行业', 
                        fontsize=14, fontweight='bold', pad=20)
            
            # 旋转x轴标签，避免重叠
            plt.xticks(rotation=45, ha='right', fontsize=10)
            
            # 设置网格线
            ax.grid(axis='y', linestyle='--', alpha=0.3)
            
            # 设置y轴从0开始，或者根据数据调整
            y_min, y_max = ax.get_ylim()
            if y_min > 0:
                ax.set_ylim(bottom=0)
            elif y_max < 0:
                ax.set_ylim(top=0)
            
            # 添加零线参考线
            ax.axhline(y=0, color='gray', linestyle='-', linewidth=0.5, alpha=0.5)
            
            # 调整布局，避免标签被截断
            plt.tight_layout()
        else:
            st.warning(f"{display_year}年没有数据")
    
    return df_sum, fig, available_years

def display_financial_analysis():
    """
    在Streamlit中显示财务分析结果
    """
    st.subheader('📊 申万一级行业财务统计')
    st.markdown("**实训3内容：** 仅考虑申万一级行业统计，包括营收和利润统计")
    
    # 创建两列布局
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        # 选择分析类型
        analysis_type = st.selectbox(
            "选择分析类型",
            ['营业收入', '营业利润'],
            key='finance_analysis_type'
        )
    
    # 先执行一次分析获取可用年份
    with st.spinner("正在加载数据..."):
        df_sum, _, available_years = perform_financial_analysis(
            analysis_type=analysis_type,
            level="新版一级行业",
            show_chart=False
        )
    
    if df_sum is not None:
        with col2:
            # 选择年份
            if available_years:
                # 默认选择最新年份
                default_year = max(available_years)
                selected_year = st.selectbox(
                    "选择年份",
                    options=available_years,
                    index=available_years.index(default_year) if default_year in available_years else 0,
                    key='finance_year_selection'
                )
            else:
                selected_year = None
                st.info("无可用年份数据")
        
        # 重新执行分析，使用选择的年份
        with st.spinner(f"正在分析{analysis_type}数据..."):
            df_sum, fig, _ = perform_financial_analysis(
                analysis_type=analysis_type,
                level="新版一级行业",
                show_chart=True,
                selected_year=selected_year
            )
        
        # 显示数据表
        st.subheader(f'📈 {analysis_type}行业概况')
        
        # 格式化显示
        display_df = df_sum.copy()
        display_df[analysis_type] = display_df[analysis_type].apply(lambda x: f"{x:,.2f}")
        display_df[f"{analysis_type}增长率"] = display_df[f"{analysis_type}增长率"].apply(lambda x: f"{x:.2f}%")
        display_df["上市公司家数"] = display_df["上市公司家数"].astype(int)
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        # 显示图表
        if fig is not None:
            st.subheader(f'📊 {analysis_type}增长率最高的8个行业')
            st.pyplot(fig)
            
            # 提供数据下载
            st.markdown("---")
            csv = df_sum.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📥 下载行业财务数据 (CSV)",
                data=csv,
                file_name=f"行业财务分析_{analysis_type}_{selected_year}.csv",
                mime="text/csv"
            )
            
            # 添加所有年份对比的选项
        with st.expander("📈 查看多年对比"):
            st.markdown("### 多年增长率对比")
            
            # 获取所有年份的数据
            years_data = {}
            for year in available_years:
                year_df = df_sum[df_sum["年度"] == year]
                if not year_df.empty:
                    years_data[year] = year_df
            
            if len(years_data) > 1:
                # 创建多年对比图表
                fig2, ax2 = plt.subplots(figsize=(14, 7))
                
                # 获取所有年份中共同的行业（取前5个行业，避免太拥挤）
                all_industries = set()
                for year, data in years_data.items():
                    # 获取该年份增长率最高的5个行业
                    top_industries = data.nlargest(5, f"{analysis_type}增长率")["行业名称"].tolist()
                    all_industries.update(top_industries)
                
                common_industries = list(all_industries)[:5]  # 取前5个
                
                if common_industries:
                    # 准备数据
                    x = np.arange(len(common_industries))
                    width = 0.15  # 柱状图宽度
                    
                    # 使用不同的紫色调
                    colors = ['#4B0082', '#6A0DAD', '#8A2BE2', '#9370DB', '#D8BFD8', '#E6E6FA']
                    
                    # 只显示最近几年的数据，避免太拥挤
                    sorted_years = sorted(years_data.keys())
                    display_years = sorted_years[-4:] if len(sorted_years) > 4 else sorted_years  # 最多显示4年
                    
                    for idx, year in enumerate(display_years):
                        year_df = years_data[year]
                        # 获取该年份这些行业的增长率
                        values = []
                        for industry in common_industries:
                            industry_data = year_df[year_df["行业名称"] == industry]
                            if not industry_data.empty:
                                values.append(industry_data[f"{analysis_type}增长率"].values[0])
                            else:
                                values.append(0)
                        
                        # 计算每个柱子的位置
                        bar_positions = x + idx*width - width*(len(display_years)-1)/2
                        bars = ax2.bar(bar_positions, values, width, 
                                      label=f'{year}年', 
                                      color=colors[idx % len(colors)],
                                      edgecolor='white', linewidth=1)
                        
                        # 在每个柱子上方添加年份标签
                        for bar, value in zip(bars, values):
                            height = bar.get_height()
                            if height != 0:  # 只在有数据的柱子上添加标签
                                # 在柱子顶部添加年份
                                ax2.text(bar.get_x() + bar.get_width()/2, 
                                        height + (1 if height >= 0 else -3),
                                        f'{year}',
                                        ha='center', va='bottom' if height >= 0 else 'top',
                                        fontsize=8,
                                        fontweight='bold',
                                        color=colors[idx % len(colors)])
                                
                                # 在柱子内部添加数值
                                if abs(height) > 5:  # 只在数值较大时显示，避免拥挤
                                    ax2.text(bar.get_x() + bar.get_width()/2, 
                                            height/2 if height > 0 else height*0.7,
                                            f'{height:.1f}%',
                                            ha='center', va='center',
                                            fontsize=8,
                                            fontweight='bold',
                                            color='white')
                    
                    ax2.set_xlabel('行业名称', fontsize=12)
                    ax2.set_ylabel(f'{analysis_type}增长率（%）', fontsize=12)
                    ax2.set_title(f'{analysis_type}增长率多年对比（Top{len(common_industries)}行业）', 
                                 fontsize=14, fontweight='bold')
                    ax2.set_xticks(x)
                    ax2.set_xticklabels(common_industries, rotation=45, ha='right', fontsize=10)
                    
                    # 添加图例
                    ax2.legend(loc='upper right', fontsize=10)
                    
                    # 添加网格线
                    ax2.grid(axis='y', linestyle='--', alpha=0.3)
                    
                    # 添加零线
                    ax2.axhline(y=0, color='gray', linestyle='-', linewidth=0.5, alpha=0.5)
                    
                    # 调整布局
                    plt.tight_layout()
                    st.pyplot(fig2)
    else:
        st.error("无法获取财务分析数据")
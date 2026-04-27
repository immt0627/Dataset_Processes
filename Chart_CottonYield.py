# @Descripttion ：
# -*- codeing: utf-8 -*-
# @time ：2026/4/1 23:52
# @Author : Yi Liu
# @Site :
# @file : Chart_CottonYield.py
# @Sofeware : VScode

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt, cm




file_path="CottonYield.csv"
Cotton_Yield = pd.read_csv(file_path, encoding='utf-8')

# 删除seed_cotton_yield_average(kg/mu)列没有数据的行
Cotton_Yield = Cotton_Yield.dropna(subset=['seed_cotton_yield_average(kg/mu) '])

# 获取所有唯一的年份
years = Cotton_Yield['year'].unique()

# 定义不同年份使用的颜色映射
color_maps = {
    2023: 'Greens',
    2024: 'Blues',
    2025: 'Oranges'
}

# 为每个年份生成一个图表
for year in years:
    # 提取当前年份的数据
    year_data = Cotton_Yield[Cotton_Yield['year'] == year]

    # 提取处理名称和产量数据
    Cotton_production = pd.DataFrame({
        'Treatment': year_data['treatment'],
        'Yield': year_data['seed_cotton_yield_average(kg/mu) ']
    })

    # 去重，确保每个处理只有一个产量值
    Cotton_production = Cotton_production.drop_duplicates(subset=['Treatment'])

    # 按产量排序
    Cotton_production = Cotton_production.sort_values(by='Yield', ascending=True)

    # 增加图表高度以避免纵坐标标签重合
    fig, ax = plt.subplots(figsize=(14, 16))

    # 根据年份选择颜色映射，如果年份不在预定义中则使用默认颜色
    color_map_name = color_maps.get(year, 'Greens')
    colors = [getattr(cm, color_map_name)(i) for i in np.linspace(0.2, 1, len(Cotton_production))]

    # 绘制水平条形图
    bars = ax.barh(Cotton_production['Treatment'], Cotton_production['Yield'], color=colors)

    # 添加数据标签
    for bar in bars:
        width = bar.get_width()
        y_pos = bar.get_y() + bar.get_height() / 2
        # 调整文本位置，避免数字重合
        ax.text(width + 5, y_pos, f'{width:.1f}', va='center', ha='left', fontsize=10)

    # 设置图表样式
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.title(f'Cotton - Treatment - Yield ({year})', fontsize=16)  # 标题包含年份
    plt.xlabel('Yield (kg/mu)', fontsize=12)  # x轴标签
    plt.ylabel('Treatment', fontsize=12)  # y轴标签

    plt.xticks(fontsize=10)
    plt.yticks(fontsize=9)  # 增大纵坐标标签字体大小

    # 保存图表，文件名包含年份
    plt.savefig(f'image/Cotton_yield_{year}.pdf', format='pdf')
    plt.close()  # 关闭当前图表，避免内存占用

# @Descripttion ：
# -*- codeing: utf-8 -*-
# @time ：2026/4/1 23:38
# @Author : Yi Liu
# @Site :
# @file : generate_weather_chart.py
# @Sofeware : VScode

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

# 定义要处理的文件路径列表
file_paths = [
    {'path': './weather_changji.csv', 'location': 'changji'},
    {'path': './weather_kashi.csv', 'location': 'kashi'}
]

# 设置图表风格
plt.style.use('ggplot')

# 遍历处理每个文件
for file_info in file_paths:
    file_path = file_info['path']
    location = file_info['location']
    
    # 读取数据
    df = pd.read_csv(file_path)
    
    # 提取年份
    df['year'] = pd.to_datetime(df['date']).dt.year
    
    # 按年份分组，计算平均值
    yearly_avg = df.groupby('year').agg({
        'tmax(°C)': 'mean',
        'tmin(°C)': 'mean',
        'rain(mm/day)': 'mean',
        'srad(MJ/(m2*day))': 'mean'
    }).reset_index()
    
    # ===================== 1. 年平均最高温度 独立图表 =====================
    plt.figure(figsize=(8, 6))
    plt.plot(yearly_avg['year'], yearly_avg['tmax(°C)'], color='red', linewidth=1)
    plt.fill_between(yearly_avg['year'], yearly_avg['tmax(°C)'], alpha=0.3, color='red')
    plt.title(f'Average annual maximum temperature - {location}')
    plt.ylabel('Tmax (°C)')
    plt.xlabel('Years')
    plt.xticks(np.arange(1981, 2024, 6))
    plt.text(0.5, -0.15, '(a) Maximum daily temperature', ha='center', va='center', transform=plt.gca().transAxes)
    plt.savefig(f'image/{location}_1_tmax_chart.png', dpi=300, bbox_inches='tight')
    plt.close()  # 关闭图表，释放内存
    
    # ===================== 2. 年平均最低温度 独立图表 =====================
    plt.figure(figsize=(8, 6))
    plt.plot(yearly_avg['year'], yearly_avg['tmin(°C)'], color='red', linewidth=1)
    plt.fill_between(yearly_avg['year'], yearly_avg['tmin(°C)'], alpha=0.3, color='red')
    plt.title(f'Average annual minimum temperature - {location}')
    plt.ylabel('Tmin (°C)')
    plt.xlabel('Years')
    plt.xticks(np.arange(1981, 2024, 6))
    plt.text(0.5, -0.15, '(b) Minimum daily temperature', ha='center', va='center', transform=plt.gca().transAxes)
    plt.savefig(f'image/{location}_2_tmin_chart.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # ===================== 3. 年平均降雨量 独立图表 =====================
    plt.figure(figsize=(8, 6))
    plt.plot(yearly_avg['year'], yearly_avg['rain(mm/day)'], color='blue', linewidth=1)
    plt.title(f'Average annual Rainfall - {location}')
    plt.ylabel('Rain (mm/day)')
    plt.xlabel('Years')
    plt.xticks(np.arange(1981, 2024, 6))
    plt.text(0.5, -0.15, '(c) Daily rainfall', ha='center', va='center', transform=plt.gca().transAxes)
    plt.savefig(f'image/{location}_3_rain_chart.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # ===================== 4. 年平均太阳辐射 独立图表 =====================
    plt.figure(figsize=(8, 6))
    plt.plot(yearly_avg['year'], yearly_avg['srad(MJ/(m2*day))'], color='green', linewidth=1, linestyle='--')
    plt.title(f'Average annual solar radiation - {location}')
    plt.ylabel('SRAD (MJ/(m2*day))')
    plt.xlabel('Years')
    plt.xticks(np.arange(1981, 2024, 6))
    plt.text(0.5, -0.15, '(d) Daily solar radiation', ha='center', va='center', transform=plt.gca().transAxes)
    plt.savefig(f'image/{location}_4_srad_chart.png', dpi=300, bbox_inches='tight')
    plt.close()

print("8个独立图表已生成完成！")
print("保存路径：./")
print("文件名：changji_1_tmax_chart.png、changji_2_tmin_chart.png、changji_3_rain_chart.png、changji_4_srad_chart.png")
print("kashi_1_tmax_chart.png、kashi_2_tmin_chart.png、kashi_3_rain_chart.png、kashi_4_srad_chart.png")
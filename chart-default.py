# @Descripttion ：
# -*- codeing: utf-8 -*-
# @time ：2026/4/1 23:38
# @Author : Yi Liu
# @Site :
# @file : chart-default.py
# @Sofeware : VScode




import numpy as np
import pandas as pd
import matplotlib.cm as cm
import matplotlib.pyplot as plt




# -----------------------------------------------sensor time default analysis-------------------------------

def sensor_data_analysis(folder_path, didian, include_spore_insect,year):
    location_name = didian.replace("_sensor", "") if didian.endswith("_sensor") else didian
    
    ConductSensor = pd.read_csv(folder_path + f'/ConductSensor_{location_name}.csv')
    HeatFluxSensor = pd.read_csv(folder_path + f'/HeatFluxSensor_{location_name}.csv')
    HumiditySensor = pd.read_csv(folder_path + f'/HumiditySensor_{location_name}.csv')
    PHSensor = pd.read_csv(folder_path + f'/PHSensor_{location_name}.csv')
    SoilNutSensor = pd.read_csv(folder_path + f'/SoilNutSensor_{location_name}.csv')
    TemSensor = pd.read_csv(folder_path + f'/TemSensor_{location_name}.csv')

    # 根据地点和开关决定是否加载Spore和Insect传感器数据
    if didian == "changji_sensor" and include_spore_insect:
        InsectSensor = pd.read_csv(folder_path + '/InsectSensor.csv')
        SporeSensor = pd.read_csv(folder_path + '/SporeImages.csv')
        sensors =['Conduct','HeatFlux', 'Humidity','Insect','PH','SoilNut','Spore','Tem']
    else:
        sensors =['Conduct','HeatFlux', 'Humidity','PH','SoilNut','Tem']

    # 根据年份和地点设置日期范围
    if didian == "kashi_sensor":
        date_range = pd.date_range(start='2025-06-23', end='2025-09-26', freq='D').date
    elif year == 2024:
        date_range = pd.date_range(start='2024-07-01', end='2024-09-19', freq='D').date
    else:
        date_range = pd.date_range(start='2025-04-24', end='2025-09-28', freq='D').date

    continuous_data = pd.DataFrame(index=date_range,columns=[sensor for sensor in sensors])

    Cotton_ConductSensor_default = ConductSensor.loc[:, ["collect_time"]]
    Cotton_HeatFluxSensor_default = HeatFluxSensor.loc[:, ["collect_time"]]
    Cotton_HumiditySensor_default = HumiditySensor.loc[:, ["collect_time"]]
    Cotton_PHSensor_default = PHSensor.loc[:, ["collect_time"]]
    Cotton_SoilNutSensor_default = SoilNutSensor.loc[:, ["collect_time"]]
    Cotton_TemSensor_default = TemSensor.loc[:, ["collect_time"]]

    # 根据地点和开关决定是否处理Spore和Insect传感器数据
    if didian == "changji" and include_spore_insect:
        Cotton_InsectSensor_default = InsectSensor.loc[:, ["collect_time"]]
        Cotton_SporeSensor_default = SporeSensor.loc[:, ["collect_time"]]

    # 处理ConductSensor
    Cotton_ConductSensor_default['collect_time'] = pd.to_datetime(Cotton_ConductSensor_default['collect_time'], format='%Y-%m-%dT%H:%M:%SZ', errors='coerce')
    Cotton_ConductSensor_default = Cotton_ConductSensor_default[Cotton_ConductSensor_default['collect_time'].notna() & (Cotton_ConductSensor_default['collect_time'].dt.year == year)]
    Cotton_ConductSensor_default['collect_time'] = Cotton_ConductSensor_default['collect_time'].dt.date

    # 处理HeatFluxSensor
    Cotton_HeatFluxSensor_default['collect_time'] = pd.to_datetime(Cotton_HeatFluxSensor_default['collect_time'], format='%Y-%m-%dT%H:%M:%SZ', errors='coerce')
    Cotton_HeatFluxSensor_default = Cotton_HeatFluxSensor_default[Cotton_HeatFluxSensor_default['collect_time'].notna() & (Cotton_HeatFluxSensor_default['collect_time'].dt.year == year)]
    Cotton_HeatFluxSensor_default['collect_time'] = Cotton_HeatFluxSensor_default['collect_time'].dt.date

    # 处理HumiditySensor
    Cotton_HumiditySensor_default['collect_time'] = pd.to_datetime(Cotton_HumiditySensor_default['collect_time'], format='%Y-%m-%dT%H:%M:%SZ', errors='coerce')
    Cotton_HumiditySensor_default = Cotton_HumiditySensor_default[Cotton_HumiditySensor_default['collect_time'].notna() & (Cotton_HumiditySensor_default['collect_time'].dt.year == year)]
    Cotton_HumiditySensor_default['collect_time'] = Cotton_HumiditySensor_default['collect_time'].dt.date

    # 根据地点和开关决定是否处理InsectSensor
    if didian == "changji" and include_spore_insect:
        Cotton_InsectSensor_default['collect_time'] = pd.to_datetime(Cotton_InsectSensor_default['collect_time'], format='%Y-%m-%d-%H-%M-%S', errors='coerce')
        Cotton_InsectSensor_default = Cotton_InsectSensor_default[Cotton_InsectSensor_default['collect_time'].notna() & (Cotton_InsectSensor_default['collect_time'].dt.year == year)]
        Cotton_InsectSensor_default['collect_time'] = Cotton_InsectSensor_default['collect_time'].dt.date

    # 处理PHSensor
    Cotton_PHSensor_default['collect_time'] = pd.to_datetime(Cotton_PHSensor_default['collect_time'], format='%Y-%m-%dT%H:%M:%SZ', errors='coerce')
    Cotton_PHSensor_default = Cotton_PHSensor_default[Cotton_PHSensor_default['collect_time'].notna() & (Cotton_PHSensor_default['collect_time'].dt.year == year)]
    Cotton_PHSensor_default['collect_time'] = Cotton_PHSensor_default['collect_time'].dt.date

    # 处理SoilNutSensor
    Cotton_SoilNutSensor_default['collect_time'] = pd.to_datetime(Cotton_SoilNutSensor_default['collect_time'], format='%Y-%m-%dT%H:%M:%SZ', errors='coerce')
    Cotton_SoilNutSensor_default = Cotton_SoilNutSensor_default[Cotton_SoilNutSensor_default['collect_time'].notna() & (Cotton_SoilNutSensor_default['collect_time'].dt.year == year)]
    Cotton_SoilNutSensor_default['collect_time'] = Cotton_SoilNutSensor_default['collect_time'].dt.date

    # 根据地点和开关决定是否处理SporeSensor
    if didian == "changji" and include_spore_insect:
        Cotton_SporeSensor_default['collect_time'] = pd.to_datetime(Cotton_SporeSensor_default['collect_time'], format='%Y-%m-%d-%H-%M-%S', errors='coerce')
        Cotton_SporeSensor_default = Cotton_SporeSensor_default[Cotton_SporeSensor_default['collect_time'].notna() & (Cotton_SporeSensor_default['collect_time'].dt.year == year)]
        Cotton_SporeSensor_default['collect_time'] = Cotton_SporeSensor_default['collect_time'].dt.date

    # 处理TemSensor
    Cotton_TemSensor_default['collect_time'] = pd.to_datetime(Cotton_TemSensor_default['collect_time'], format='%Y-%m-%dT%H:%M:%SZ', errors='coerce')
    Cotton_TemSensor_default = Cotton_TemSensor_default[Cotton_TemSensor_default['collect_time'].notna() & (Cotton_TemSensor_default['collect_time'].dt.year == year)]
    Cotton_TemSensor_default['collect_time'] = Cotton_TemSensor_default['collect_time'].dt.date

    # 根据地点和开关决定传感器数据列表
    if didian == "changji" and include_spore_insect:
        sensors_default=[Cotton_ConductSensor_default,Cotton_HeatFluxSensor_default,
                         Cotton_HumiditySensor_default,Cotton_InsectSensor_default,
                         Cotton_PHSensor_default,Cotton_SoilNutSensor_default,Cotton_SporeSensor_default,Cotton_TemSensor_default]
    else:
        sensors_default=[Cotton_ConductSensor_default,Cotton_HeatFluxSensor_default,
                         Cotton_HumiditySensor_default,
                         Cotton_PHSensor_default,Cotton_SoilNutSensor_default,Cotton_TemSensor_default]

    for sensor ,sensor_default in zip(continuous_data.columns,sensors_default):
        for date in continuous_data.index:
            matched_rows = sensor_default[sensor_default['collect_time'] == date]
            if not matched_rows.empty:
                continuous_data.at[date, sensor] = matched_rows['collect_time'].iloc[0]

    return  continuous_data,sensors


# -----------------------------------------------Visualization of sensor time default analysis-------------------------------

# 定义要生成的图表配置列表
chart_configs = [
    {"didian": "changji_sensor", "year": 2024, "include_spore_insect": False},
    {"didian": "changji_sensor", "year": 2025, "include_spore_insect": False},
    {"didian": "kashi_sensor", "year": 2025, "include_spore_insect": False},
]

# 定义不同地点和年份组合使用的颜色映射
color_maps = {
    ("changji_sensor", 2024): 'Greens',
    ("changji_sensor", 2025): 'Blues',
    ("kashi_sensor", 2025): 'Oranges'
}

# 循环生成每个图表
for config in chart_configs:
    didian = config["didian"]
    year = config["year"]
    include_spore_insect = config["include_spore_insect"]

    folder_path = f"./{didian}"

    continuous_data,sensors = sensor_data_analysis(folder_path, didian, include_spore_insect, year)

    width_ratios = [1] * len(sensors)
    sensors = continuous_data.columns
    dates = continuous_data.index
    fig, axes = plt.subplots(nrows=1, ncols=len(sensors), figsize=(12, 6), sharey=True, width_ratios=width_ratios)

    # 根据地点和年份选择颜色映射
    color_map_name = color_maps.get((didian, year), 'Greens')
    colors = [getattr(cm, color_map_name)(np.random.normal(loc=0.9, scale=0.3, size=1)[0]) for _ in sensors]

    if len(sensors) == 1:
        axes = [axes]

    datetime_index = pd.DatetimeIndex(continuous_data.index)
    formatted_dates = datetime_index.strftime('%Y-%m-%d')

    for i,(ax, sensor,color1) in enumerate(zip(axes, sensors,colors)):
        data_presence = np.where(continuous_data[sensor].notnull(), 1, 0)
        percentage_present = int(np.mean(data_presence)*100)
        ax.barh(dates,data_presence,label=sensor, height=1, align='center', color=color1)
        ax.set_xlabel(f'{sensor}:{percentage_present}% ',fontsize=12)
        ax.set_yticks([])
        ax.set_xticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)

    num_ticks = 10
    tick_interval = len(dates) // (num_ticks - 1) if len(dates) > num_ticks else 1
    ticks = np.arange(0, len(dates), tick_interval)
    plt.yticks(dates[ticks], fontsize=10)
    fig.suptitle(f"Cotton_default_{didian}_{year}", fontsize=16)
    plt.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
    plt.tight_layout()
    plt.savefig(f'image/Cotton_default_{didian}{year}.pdf', bbox_inches='tight',format='pdf')
    print(f'image/Cotton_default_{didian}{year}.pdf saved')
    plt.close()

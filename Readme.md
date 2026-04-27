## **Data Processing and Visualization**
### 1 Introduction

This project aims to visually present cotton-related sensor data and weather data through data visualization. The folder contains the following key documents:

| **Author** | ©AuroraLab |
|:--------:   |:-------------------------------------|
| **chart-default.py** | Generates charts for cotton sensor default data (changji & kashi) |
| **generate_weather_chart.py** | Generates charts for weather data (changji & kashi, 1981-2023) |
| **Chart_CottonYield.py** | Generates charts for cotton yield data |

These charts help analyze cotton growth conditions and yield trends, providing data support for relevant research.

### **Use Note for Visualization Scripts of Cotton Field Data**

This repository contains three Python scripts for visualizing multi-source data collected from a cotton field experiment. These scripts are: `chart-default.py`, `generate_weather_chart.py`, and `Chart_CottonYield.py`. Each serves a distinct analytical purpose and requires specific datasets to be available in a predefined directory structure. Below are usage guidelines and path configuration instructions to ensure successful execution.

#### **1. Directory Structure & Path Configuration**

All scripts rely on relative file paths. Users must ensure that the project directory is organized as follows:

```
ProjectRoot/
│
├── chart-default.py
├── generate_weather_chart.py
├── Chart_CottonYield.py
├── CottonYield.csv
├── weather_changji.csv
├── weather_kashi.csv
├── changji_sensor/
│   ├── ConductSensor_changji.csv
│   ├── HeatFluxSensor_changji.csv
│   ├── HumiditySensor_changji.csv
│   ├── InsectSensor.csv
│   ├── PHSensor_changji.csv
│   ├── SoilNutSensor_changji.csv
│   ├── SporeImages.csv
│   └── TemSensor_changji.csv
│
├── kashi_sensor/
│   ├── ConductSensor_kashi.csv
│   ├── HeatFluxSensor_kashi.csv
│   ├── HumiditySensor_kashi.csv
│   ├── PHSensor_kashi.csv
│   ├── SoilNutSensor_kashi.csv
│   ├── TemSensor_kashi.csv
│   └── sensors_kashi.csv
│
└── image/                    # Output directory for generated charts
    ├── Cotton_default_changji_sensor2024.pdf
    ├── Cotton_default_changji_sensor2025.pdf
    ├── Cotton_default_kashi_sensor2025.pdf
    ├── Cotton_yield_2023.pdf
    ├── Cotton_yield_2024.pdf
    ├── Cotton_yield_2025.pdf
    ├── changji_1_tmax_chart.png
    ├── changji_2_tmin_chart.png
    ├── changji_3_rain_chart.png
    ├── changji_4_srad_chart.png
    ├── kashi_1_tmax_chart.png
    ├── kashi_2_tmin_chart.png
    ├── kashi_3_rain_chart.png
    └── kashi_4_srad_chart.png

```

**Important:** The scripts use relative paths such as `./changji_sensor/`, `./weather_changji.csv`, and `./image/`. All output charts will be saved to the `image/` folder. Ensure that you run the scripts from the project root directory, or configure your IDE (e.g., PyCharm) working directory to point to the project root.

------

#### **2. Script Functions and Data Requirements**

**`chart-default.py`**

- **Purpose:** Visualizes daily data completeness across soil/environmental sensors (conductivity, temperature, humidity, pH, etc.) for different locations and years.
- **Inputs:** Sensor CSV files from `changji_sensor/` and `kashi_sensor/` directories.
- **Outputs:** PDF charts (saved to `image/` folder):
  - `image/Cotton_default_changji_sensor2024.pdf`
  - `image/Cotton_default_changji_sensor2025.pdf`
  - `image/Cotton_default_kashi_sensor2025.pdf`

**`generate_weather_chart.py`**

- **Purpose:** Calculates and plots annual trends in solar radiation, maximum/minimum temperature, and rainfall from historical weather data.
- **Inputs:** `weather_changji.csv` and `weather_kashi.csv` containing columns such as `date`, `tmax(°C)`, `tmin(°C)`, `rain(mm/day)`, and `srad(MJ/(m2*day))`.
- **Outputs:** PNG charts for each location (saved to `image/` folder):
  - `image/changji_1_tmax_chart.png`
  - `image/changji_2_tmin_chart.png`
  - `image/changji_3_rain_chart.png`
  - `image/changji_4_srad_chart.png`
  - `image/kashi_1_tmax_chart.png`
  - `image/kashi_2_tmin_chart.png`
  - `image/kashi_3_rain_chart.png`
  - `image/kashi_4_srad_chart.png`

**`Chart_CottonYield.py`**

- **Purpose:** Compares cotton yields across different water treatment conditions.
- **Input:** `CottonYield.csv` containing treatment information and yield data.
- **Outputs:** PDF charts (saved to `image/` folder):
  - `image/Cotton_yield_2023.pdf`
  - `image/Cotton_yield_2024.pdf`
  - `image/Cotton_yield_2025.pdf`

------

#### **3. Dependencies**

Ensure the following Python libraries are installed in your environment:

```
pip install numpy pandas matplotlib
```

------

#### **4. Encoding and Format Notes**

- CSV files should be encoded in UTF-8 or ISO-8859-1 as specified in the scripts.
- Ensure date formats match `'YYYY-MM-DD HH:MM:SS'` when parsing with `pd.to_datetime`.

------

#### **5. Running the Scripts**

To ensure full compatibility and prevent relative path errors, run the scripts from the project root directory:

```
python chart-default.py
python generate_weather_chart.py
python Chart_CottonYield.py
```

Or configure the working directory in your IDE (e.g., PyCharm) to point to the project root.

### Copyright
Copyright © 2024 AuroraLab of Tsinghua University and Xinjiang University. All rights reserved. No part of this publication may be reproduced, stored in a retrieval system, or transmitted, in any form or by any means, electronic, mechanical, photocopying, recording, or otherwise, without the prior written permission of AuroraLab of Tsinghua University and Xinjiang University.
Email: heliang@mail.tsinghua.edu.cn.

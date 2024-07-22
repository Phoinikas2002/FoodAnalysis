import pandas as pd
import folium
import requests
import time

import pandas as pd
import re


def load_data(file_path, encoding='gbk'):
    """
    加载CSV文件并处理列名，去除地址列中的括号及其内容，返回DataFrame。
    """
    # 加载数据
    data = pd.read_csv(file_path, encoding=encoding)

    # 处理列名
    data.columns = data.columns.str.strip()

    # 去除地址列中的括号及其内容
    if '地址' in data.columns:
        data['地址'] = data['地址'].apply(lambda x: re.sub(r'\（.*?\）', '', x).strip())

    return data


import requests

def get_location(address, key):
    """
    使用高德地图API获取地址的经纬度。
    """
    url = 'https://restapi.amap.com/v3/geocode/geo'
    params = {
        'key': key,
        'address': address,
        'output': 'json'
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()
        if data['status'] == '1' and data['geocodes']:
            location = data['geocodes'][0]
            return (float(location['location'].split(',')[1]), float(location['location'].split(',')[0]))
        else:
            print(f"无法解析地址: {address}")
            return (None, None)
    except requests.RequestException as e:
        print(f"地理编码错误: {e}")
        return (None, None)



def create_map(data, key):
    """
    创建标记商家的地图，标记点的颜色深浅表示受欢迎程度。
    """
    # 创建简约样式的地图对象，中心设为成都的经纬度
    city_map = folium.Map(location=[30.65787, 104.06584], zoom_start=12, tiles='cartodb positron')

    # 添加商家标记
    for _, row in data.iterrows():
        location = get_location(row['地址'], key)
        if location[0] is not None:
            # 根据受欢迎程度设置标记的颜色
            color = 'red' if row['总分数'] >= 9.9 else 'orange' if row['总分数'] >= 9.5 else 'green' if row[
                                                                                                             '总分数'] >= 9.0 else 'blue'

            # 使用Icon标记
            folium.Marker(
                location=[location[0], location[1]],
                icon=folium.Icon(color=color, icon='info-sign', icon_color='transparent', prefix='glyphicon'),  # 你可以选择不同的图标
                popup=folium.Popup(f"<b>店名:</b> {row['店名']}<br><b>总分数:</b> {row['总分数']}", max_width=300)
            ).add_to(city_map)
        else:
            print(f"无法解析地址: {row['地址']}")

    # 添加图例
    legend_html = """
    <div style="position: fixed; bottom: 50px; left: 50px; width: 220px; height: auto; border:2px solid grey; background:white; z-index:9999; font-size:14px; padding: 10px; border-radius: 5px; box-shadow: 0px 0px 5px rgba(0,0,0,0.3);">
        <b>受欢迎程度图例</b> <br><br>
        <div style="display: flex; align-items: center; margin-bottom: 5px;">
            <div style="width: 15px; height: 15px; background-color: blue; margin-right: 10px;"></div>
            <span>总分数 ≥ 9.9</span>
        </div>
        <div style="display: flex; align-items: center; margin-bottom: 5px;">
            <div style="width: 15px; height: 15px; background-color: green; margin-right: 10px;"></div>
            <span>9.5 ≤ 总分数 < 9.9</span>
        </div>
        <div style="display: flex; align-items: center; margin-bottom: 5px;">
            <div style="width: 15px; height: 15px; background-color: orange; margin-right: 10px;"></div>
            <span>9.0 ≤ 总分数 < 9.5</span>
        </div>
        <div style="display: flex; align-items: center;">
            <div style="width: 15px; height: 15px; background-color: red; margin-right: 10px;"></div>
            <span>总分数 < 9.0</span>
        </div>
    </div>
    """
    city_map.get_root().html.add_child(folium.Element(legend_html))

    # 保存地图到文件
    output_file = 'analysis/popular_merchants_map.html'
    city_map.save(output_file)
    print(f"地图已保存到文件: {output_file}")


def main():
    # 加载数据
    file_path = 'analysis/most_popular.csv'
    data = load_data(file_path, encoding='utf-8')

    # 高德地图API Key
    amap_key = '5b0d9c6791b5af81da6e6f1c45a88fb0'

    # 创建地图
    create_map(data, amap_key)


if __name__ == "__main__":
    main()

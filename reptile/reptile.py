import csv
import os
import time
import requests
import parsel

# 打开 CSV 文件
file_path = '美食.csv'
f = open(file_path, mode='a', encoding='utf-8', newline='')

# 定义 csv.DictWriter 对象
csv_writer = csv.DictWriter(f, fieldnames=[
    '店名',
    '评论',
    '人均消费',
    '口味',
    '环境',
    '服务',
    '电话',
    '地址',
    '详情页'
])

# 写入表头
csv_writer.writeheader()

base_url = "https://www.dianping.com/chengdu/ch10"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
    'Host': 'www.dianping.com',
    'Referer': 'https://www.dianping.com/chengdu',
    'Cookie': '_lx_utm=utm_source%3Dbing%26utm_medium%3Dorganic; _lxsdk_cuid=190bfd60b2ac8-0313229a11a681-4c657b58-144000-190bfd60b2bc8; _lxsdk=190bfd60b2ac8-0313229a11a681-4c657b58-144000-190bfd60b2bc8; _hc.v=bbd8a2ee-faa3-57a4-6553-227ae516da21.1721205397; WEBDFPID=z6z164213x82511510zyzv668y0v1vw5809yuw373w79795823w746x1-2036565397825-1721205394287CGCEQWAfd79fef3d01d5e9aadc18ccd4d0c95072775; qruuid=61fa7515-6bcb-4569-86ec-3835c3ec200f; dper=0202c326edc7b0d807ad563f67c3e7914063d4230e1f2c8a80612c88f313e2a1624ecb676cfdba81be434fd76553251fe0f7e5ff768ad990eda70000000050210000de76b4e4e85ec6102cda91ca33b768d4e0349031a5be148c67cc6d74b3cc5a3e63698234dce81af3bfd89ee217bd6b00; ll=7fd06e815b796be3df069dec7836c3df; ua=dpuser_2095584349; ctu=04b3cb4b634b2b790cd3bafb179d977bd7cffb7968ee27f72befa679f67bda4b; dplet=3c5fd8e3876f5e263399d95d314f7ef7; Hm_lvt_602b80cf8079ae6591966cc70a3940e7=1721206746; HMACCOUNT=3EF3AF2A380947C1; fspop=test; cy=8; cye=chengdu; s_ViewType=10; Hm_lpvt_602b80cf8079ae6591966cc70a3940e7=1721217612; _lxsdk_s=190c08d2eb2-81b-371-107%7C%7C42',
}

data_count = 0  # 用于计数实际写入的数据条数

for page in range(1, 100):  # 爬取前2页的数据
    if page == 1:
        url = base_url
    else:
        url = f"{base_url}/p{page}"

    response = requests.get(url=url, headers=headers)

    if response.status_code == 403:
        print("初始请求被禁止（403）。请检查是否需要额外的请求头或Cookies。")
        continue
    else:
        print(f"请求第 {page} 页状态码：{response.status_code}")

    selector = parsel.Selector(response.text)
    href = selector.css('.shop-list ul li .pic a::attr(href)').getall()

    print(f"第 {page} 页获取的详情页链接数量：{len(href)}")
    print(f"第 {page} 页详情页链接列表：{href}")

    for index in href:
        retry_count = 0  # 初始化重试计数器
        max_retries = 5  # 最大重试次数
        while retry_count < max_retries:
            try:
                html_data = requests.get(url=index, headers=headers)
                if html_data.status_code == 403:
                    print(f"请求 {index} 被禁止（403），正在等待重试...")
                    retry_count += 1
                    time.sleep(5)  # 等待5秒后重试
                    continue
                else:
                    break
            except requests.exceptions.RequestException as e:
                print(f"请求 {index} 出现异常：{e}")
                retry_count += 1
                time.sleep(5)  # 等待5秒后重试

        if retry_count == max_retries:
            print(f"请求 {index} 重试超过最大次数，跳过该请求。")
            continue

        selector_1 = parsel.Selector(html_data.text)
        title = selector_1.css('.shop-name::text').get()  # 店名
        count = selector_1.css('#reviewCount::text').get()  # 评论
        price = selector_1.css('#avgPriceTitle::text').get()  # 人均消费
        item_list = selector_1.css('#comment_score .item::text').getall()  # 评价

        if len(item_list) >= 3:
            taste = item_list[0].split(': ')[-1]  # 口味评分
            environment = item_list[1].split(': ')[-1]  # 环境评分
            service = item_list[2].split(': ')[-1]  # 服务评分
        else:
            taste = environment = service = 'N/A'

        address = selector_1.css('#address::text').get()  # 地址
        tel_list = selector_1.css('.tel::text').getall()
        tel = tel_list[-1] if tel_list else 'N/A'  # 电话

        dit = {
            '店名': title,
            '评论': count,
            '人均消费': price,
            '口味': taste,
            '环境': environment,
            '服务': service,
            '电话': tel,
            '地址': address,
            '详情页': index
        }

        csv_writer.writerow(dit)
        data_count += 1  # 每写入一条数据，计数器加1

f.close()

# 检查文件是否只有表头
if data_count == 0:
    os.remove(file_path)
    print("实际没有爬取到数据，已删除文件")
else:
    print("数据爬取完毕并写入美食.csv文件")

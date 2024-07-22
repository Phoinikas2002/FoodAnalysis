import csv
import time
import requests
import parsel

# 打开 CSV 文件
f = open('美食.csv', mode='a', encoding='utf-8', newline='')

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

url = "https://www.dianping.com/search/keyword/9/0_%E7%BE%8E%E9%A3%9F"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
    'Cookie': 'fspop=test; _lxsdk_cuid=190958ad652c8-00eb683a666af6-26001f51-144000-190958ad652c8; _lxsdk=190958ad652c8-00eb683a666af6-26001f51-144000-190958ad652c8; _hc.v=6e9c5d52-5b67-d982-124d-720b0b7100d8.1720495822; WEBDFPID=xw13y2w560045621y68u120z74y667vy809041zuy6y97958872yvxx7-2035855833060-1720495833060WOUCEQQfd79fef3d01d5e9aadc18ccd4d0c95077422; qruuid=8e13393b-d570-4935-b05e-7848cdd1768c; dplet=7fb82b432f0b21b744e0d50de6263a9f; dper=020297207deb3fa2da0a40726d65f29360bc69c15811dbabfc9bc39086774c2662278cb106973ed611a3adf72d1986977278c22bf52eb1cf997a0000000050210000bd2815d540d31aca04b045bfb4f0387c50ad9abfcd24f59128b537c91610511c3d621e6b4b6680718d20cb15cc7de82e; ua=cippleboli; ctu=43c3f77a6d4382acab103603eb72cf1798ae669a55712dec944264c32e8b3bbf; s_ViewType=10; ll=7fd06e815b796be3df069dec7836c3df; Hm_lvt_602b80cf8079ae6591966cc70a3940e7=1720495888,1720577401,1720941860; HMACCOUNT=56D165435C6CA31C; _lx_utm=utm_source%3Dgoogle%26utm_medium%3Dorganic; cy=9; cye=chongqing; Hm_lpvt_602b80cf8079ae6591966cc70a3940e7=1720957807; _lxsdk_s=190b110a0fa-4a2-5a7-772%7C%7C130',
    'Host': 'www.dianping.com',
    'Referer': 'https://www.dianping.com/chongqing'
}


response = requests.get(url=url, headers=headers)

if response.status_code == 403:
    print("初始请求被禁止（403）。请检查是否需要额外的请求头或Cookies。")
else:
    print(f"初始请求状态码：{response.status_code}")

selector = parsel.Selector(response.text)
href = selector.css('.shop-list ul li .pic a::attr(href)').getall()

print(f"获取的详情页链接数量：{len(href)}")
print(f"详情页链接列表：{href}")



for index in href:
    while True:
        try:
            html_data = requests.get(url=index, headers=headers)
            if html_data.status_code == 403:
                print(f"请求 {index} 被禁止（403），正在等待重试...")
                time.sleep(5)  # 等待5秒后重试
                continue
            else:
                break
        except requests.exceptions.RequestException as e:
            print(f"请求 {index} 出现异常：{e}")
            time.sleep(5)  # 等待5秒后重试

    selector_1 = parsel.Selector(html_data.text)
    title = selector_1.css('.shop-name::text').get()  # 店名
    count = selector_1.css('#reviewCount::text').get()  # 评论
    price = selector_1.css('#avgPriceTitle::text').get()  # 人均消费
    item_list = selector_1.css('#comment_score .item::text').getall()  # 评价

    if len(item_list) >= 3:
        taste = item_list[0].split(': ')[-1]  # 口味评分
        environment = item_list[1].split(': ')[-1]  # 环境评分
        service = item_list[-1].split(': ')[-1]  # 服务评分
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

f.close()
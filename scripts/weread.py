# -*- coding: utf-8 -*-

import argparse
import json
import logging
import os
import re
import time
from notion_client import Client
import requests
from requests.utils import cookiejar_from_dict
from http.cookies import SimpleCookie
from datetime import datetime
import hashlib
from dotenv import load_dotenv
import os
from utils import (
    get_callout,
    get_date,
    get_file,
    get_heading,
    get_icon,
    get_multi_select,
    get_number,
    get_quote,
    get_rich_text,
    get_select,
    get_table_of_contents,
    get_title,
    get_url,
)
load_dotenv()
WEREAD_URL = "https://weread.qq.com/"
WEREAD_NOTEBOOKS_URL = "https://i.weread.qq.com/user/notebooks"
WEREAD_BOOKMARKLIST_URL = "https://i.weread.qq.com/book/bookmarklist"
WEREAD_CHAPTER_INFO = "https://i.weread.qq.com/book/chapterInfos"
WEREAD_READ_INFO_URL = "https://i.weread.qq.com/book/readinfo"
WEREAD_REVIEW_LIST_URL = "https://i.weread.qq.com/review/list"
WEREAD_BOOK_INFO = "https://i.weread.qq.com/book/info"


def parse_cookie_string(cookie_string):
    cookie = SimpleCookie()
    cookie.load(cookie_string)
    cookies_dict = {}
    cookiejar = None
    for key, morsel in cookie.items():
        cookies_dict[key] = morsel.value
        cookiejar = cookiejar_from_dict(cookies_dict, cookiejar=None, overwrite=True)
    return cookiejar


def get_bookmark_list(bookId):
    """获取我的划线"""
    params = dict(bookId=bookId)
    r = session.get(WEREAD_BOOKMARKLIST_URL, params=params)
    if r.ok:
        # print(f"000{r.json()}")

        # 提取 updated 列表和 refMpInfos 列表
        updated = r.json().get("updated", [])
        refMpInfos = {info["reviewId"]: info["title"] for info in r.json().get("refMpInfos", [])}

        # 添加对应的 title
        for item in updated:
            refMpReviewId = item.get("refMpReviewId")
            item["title"] = refMpInfos.get(refMpReviewId, "")
            # item["chapterUid"] = "1"
            # item["level"] = "1"

        # 返回的结果
        result = updated
        # print(json.dumps(result, ensure_ascii=False, indent=2))

        # {'synckey': 1731849521, 'updated': [{'bookId': 'MP_WXS_3079395914', 'style': 0, 'bookmarkId': 'MP_WXS_3079395914_O-ou-GeV4jWwNOwHPDQkZQ_1733-1792', 'bookVersion': 0, 'range': '1733-1792', 'markText': '以杭州的人口和经济体量，每月成交量超过6000套就是及格线，8000套以上算是良好水平，超过10000套则是优秀水平。', 'colorStyle': 0, 'type': 1, 'createTime': 1731849521, 'refMpReviewId': 'MP_WXS_3079395914_O-ou-GeV4jWwNOwHPDQkZQ'}, {'bookId': 'MP_WXS_3079395914', 'style': 0, 'bookmarkId': 'MP_WXS_3079395914_O-ou-GeV4jWwNOwHPDQkZQ_1676-1709', 'bookVersion': 0, 'range': '1676-1709', 'markText': '二手房价格真正意义上的上涨，需要成交量维持在一定的水平，有量才有价', 'colorStyle': 0, 'type': 1, 'createTime': 1731848507, 'refMpReviewId': 'MP_WXS_3079395914_O-ou-GeV4jWwNOwHPDQkZQ'}, {'bookId': 'MP_WXS_3079395914', 'style': 0, 'bookmarkId': 'MP_WXS_3079395914_O-ou-GeV4jWwNOwHPDQkZQ_3385-3434', 'bookVersion': 0, 'range': '3385-3434', 'markText': '以目前的政策力度，似乎还达不到。需要继续降息，并在明年3月全国两会上出台更多增量政策，才能有效果。', 'colorStyle': 0, 'type': 1, 'createTime': 1731847979, 'refMpReviewId': 'MP_WXS_3079395914_O-ou-GeV4jWwNOwHPDQkZQ'}, {'bookId': 'MP_WXS_3079395914', 'style': 0, 'bookmarkId': 'MP_WXS_3079395914_LVUH7KAEQoZr1Ysig1dPXQ_588-665', 'bookVersion': 0, 'range': '588-665', 'markText': '财政部所说的“美元主权债券”，并非真正的美债，而是国际市场按美元计价发行，用国家主权做担保的债券。如果是中国发行的美元债，一般也称“中国美元主权债券”。\n', 'colorStyle': 0, 'type': 1, 'createTime': 1731813565, 'refMpReviewId': 'MP_WXS_3079395914_LVUH7KAEQoZr1Ysig1dPXQ'}, {'bookId': 'MP_WXS_3079395914', 'style': 0, 'bookmarkId': 'MP_WXS_3079395914_LVUH7KAEQoZr1Ysig1dPXQ_529-571', 'bookVersion': 0, 'range': '529-571', 'markText': '不缺钱的中国，为啥要去沙特发债，而且发行的又是“美元债”？我们到底看中了沙特的什么？', 'colorStyle': 0, 'type': 1, 'createTime': 1731813542, 'refMpReviewId': 'MP_WXS_3079395914_LVUH7KAEQoZr1Ysig1dPXQ'}, {'bookId': 'MP_WXS_3079395914', 'style': 0, 'bookmarkId': 'MP_WXS_3079395914_LVUH7KAEQoZr1Ysig1dPXQ_414-426', 'bookVersion': 0, 'range': '414-426', 'markText': '中国将卖给沙特“美债”。', 'colorStyle': 0, 'type': 1, 'createTime': 1731813529, 'refMpReviewId': 'MP_WXS_3079395914_LVUH7KAEQoZr1Ysig1dPXQ'}, {'bookId': 'MP_WXS_3079395914', 'style': 0, 'bookmarkId': 'MP_WXS_3079395914_SEa0M2gqib8-Rjxl73AAxw_3776-3833', 'bookVersion': 1731689635, 'range': '3776-3833', 'markText': '在“国补”的带动下，各品类迎来全面的增长爆发，比如家电赛道GMV爆发增长142%、家居家装GMV爆发增长149%。', 'colorStyle': 0, 'type': 1, 'createTime': 1731768088, 'refMpReviewId': 'MP_WXS_3079395914_SEa0M2gqib8-Rjxl73AAxw'}, {'bookId': 'MP_WXS_3079395914', 'style': 0, 'bookmarkId': 'MP_WXS_3079395914_SEa0M2gqib8-Rjxl73AAxw_1938-2011', 'bookVersion': 1731689635, 'range': '1938-2011', 'markText': '在抖音，有140多个骑行俱乐部和200多个跑团；类似垂钓这种拥有庞大用户基础的兴趣圈层超过5000个，其中有600多个正以超50%的速度快速增长。', 'colorStyle': 0, 'type': 1, 'createTime': 1731767925, 'refMpReviewId': 'MP_WXS_3079395914_SEa0M2gqib8-Rjxl73AAxw'}, {'bookId': 'MP_WXS_3079395914', 'style': 0, 'bookmarkId': 'MP_WXS_3079395914_SEa0M2gqib8-Rjxl73AAxw_1804-1914', 'bookVersion': 1731689635, 'range': '1804-1914', 'markText': '而且这三项户外活动，已进阶成一种社交“硬通货”。抖音平台上，“原来钓鱼才是抖音运动顶流”“让骑行成为一种生活”“马拉松”等兴趣内容，成为不少用户的热议话题，相关视频播放量分别达到1905亿、418.2亿和406.6亿次。', 'colorStyle': 0, 'type': 1, 'createTime': 1731767910, 'refMpReviewId': 'MP_WXS_3079395914_SEa0M2gqib8-Rjxl73AAxw'}, {'bookId': 'MP_WXS_3079395914', 'style': 0, 'bookmarkId': 'MP_WXS_3079395914_SEa0M2gqib8-Rjxl73AAxw_1688-1721', 'bookVersion': 1731689635, 'range': '1688-1721', 'markText': '过去被视为中老年“三宝”的垂钓、骑行和跑步，如今成了年轻人的新宠。', 'colorStyle': 0, 'type': 1, 'createTime': 1731767892, 'refMpReviewId': 'MP_WXS_3079395914_SEa0M2gqib8-Rjxl73AAxw'}, {'bookId': 'MP_WXS_3079395914', 'style': 0, 'bookmarkId': 'MP_WXS_3079395914_SEa0M2gqib8-Rjxl73AAxw_387-466', 'bookVersion': 1731689635, 'range': '387-466', 'markText': '其实，今年的双11，抖音电商交出了名为“强劲增长”的成绩单。\n\n▶▷商家生意在爆发，超3.3万个品牌成交额同比翻倍，近1.7万个品牌成交额同比增速超500%。', 'colorStyle': 0, 'type': 1, 'createTime': 1731767754, 'refMpReviewId': 'MP_WXS_3079395914_SEa0M2gqib8-Rjxl73AAxw'}, {'bookId': 'MP_WXS_3079395914', 'style': 0, 'bookmarkId': 'MP_WXS_3079395914_SEa0M2gqib8-Rjxl73AAxw_237-275', 'bookVersion': 1731689635, 'range': '237-275', 'markText': '◎\xa0鲨鱼裤、设计师女装、冲锋衣的成交额，同比增长达到97%、65%和50%。', 'colorStyle': 0, 'type': 1, 'createTime': 1731767741, 'refMpReviewId': 'MP_WXS_3079395914_SEa0M2gqib8-Rjxl73AAxw'}, {'bookId': 'MP_WXS_3079395914', 'style': 0, 'bookmarkId': 'MP_WXS_3079395914_SEa0M2gqib8-Rjxl73AAxw_59-98', 'bookVersion': 1731689635, 'range': '59-98', 'markText': '“今年双11，消费者青睐的‘新三样’，是运动户外潮品、毛孩子用品和大小家电。”', 'colorStyle': 0, 'type': 1, 'createTime': 1731767729, 'refMpReviewId': 'MP_WXS_3079395914_SEa0M2gqib8-Rjxl73AAxw'}, {'bookId': 'MP_WXS_3079395914', 'style': 0, 'bookmarkId': 'MP_WXS_3079395914_zwAP0a86vIEXr8JF0zgYoQ_3847-3915', 'bookVersion': 1731457718, 'range': '3847-3915', 'markText': '近30年来，中国赶上了互联网革命的头班车，也成为了被互联网改造最彻底的国家。尤其在应用层面，中国庞大的市场和消费群体，是最好的战略资源。', 'colorStyle': 0, 'type': 1, 'createTime': 1731472866, 'refMpReviewId': 'MP_WXS_3079395914_zwAP0a86vIEXr8JF0zgYoQ'}, {'bookId': 'MP_WXS_3079395914', 'style': 0, 'bookmarkId': 'MP_WXS_3079395914_zwAP0a86vIEXr8JF0zgYoQ_3741-3808', 'bookVersion': 1731457718, 'range': '3741-3808', 'markText': '去年11月，也就是一年前，比尔·盖茨发表了一篇文章，他说：“在五年内，每个人都将拥有自己的AI私人助理，它将彻底改变我们的生活方式。”', 'colorStyle': 0, 'type': 1, 'createTime': 1731472853, 'refMpReviewId': 'MP_WXS_3079395914_zwAP0a86vIEXr8JF0zgYoQ'}, {'bookId': 'MP_WXS_3079395914', 'style': 0, 'bookmarkId': 'MP_WXS_3079395914_zwAP0a86vIEXr8JF0zgYoQ_3133-3302', 'bookVersion': 1731457718, 'range': '3133-3302', 'markText': '“比如说直播间卖手串。这种商品，外观上看都长一个样子，有人卖29，有人卖299，玄学在哪？材质结构不同，这靠图文肯定解决不了，就得在直播间靠真人来说。还有比如你卖羊毛衫，得有模特试穿，需要镜头远近来回切，以及当场做一些烧绒试验吸引眼球；或者你卖乐器，卖吉他，弹一下，听听音色，这些还都需要真人来完成。稀里糊涂用AI代替人，就等同于被割。”', 'colorStyle': 0, 'type': 1, 'createTime': 1731472808, 'refMpReviewId': 'MP_WXS_3079395914_zwAP0a86vIEXr8JF0zgYoQ'}, {'bookId': 'MP_WXS_3079395914', 'style': 0, 'bookmarkId': 'MP_WXS_3079395914_zwAP0a86vIEXr8JF0zgYoQ_2982-3033', 'bookVersion': 1731457718, 'range': '2982-3033', 'markText': '王炜也直言不讳地说：“就是割韭菜啊，特别是那些工厂，那帮人没有做内容、做运营的能力，是被割的重灾区。”', 'colorStyle': 0, 'type': 1, 'createTime': 1731472783, 'refMpReviewId': 'MP_WXS_3079395914_zwAP0a86vIEXr8JF0zgYoQ'}, {'bookId': 'MP_WXS_3079395914', 'style': 0, 'bookmarkId': 'MP_WXS_3079395914_zwAP0a86vIEXr8JF0zgYoQ_2483-2579', 'bookVersion': 1731457718, 'range': '2483-2579', 'markText': '“AI无法精准即答，也不能像人类主播一样调动情绪，在关键时刻进行‘逼单’等操作。我身边有朋友尝试过用AI做录播，模仿同行，结果别家真人一天卖十几万，AI只卖了三四百块，电费和设备钱都赚不回来。', 'colorStyle': 0, 'type': 1, 'createTime': 1731472738, 'refMpReviewId': 'MP_WXS_3079395914_zwAP0a86vIEXr8JF0zgYoQ'}, {'bookId': 'MP_WXS_3079395914', 'style': 0, 'bookmarkId': 'MP_WXS_3079395914_zwAP0a86vIEXr8JF0zgYoQ_2361-2462', 'bookVersion': 1731457718, 'range': '2361-2462', 'markText': '“比如说我卖衣服，核心卖点是图案，AI可以做落地页和背景视频，但吸引人的头图和视频，还得实拍。我们测过，AI的跳出率会高出一截，数据差了平台就不给流量，没竞争力。兜兜转转一圈，还得去找网红试穿打广告。”', 'colorStyle': 0, 'type': 1, 'createTime': 1731472702, 'refMpReviewId': 'MP_WXS_3079395914_zwAP0a86vIEXr8JF0zgYoQ'}, {'bookId': 'MP_WXS_3079395914', 'style': 0, 'bookmarkId': 'MP_WXS_3079395914_zwAP0a86vIEXr8JF0zgYoQ_2177-2206', 'bookVersion': 1731457718, 'range': '2177-2206', 'markText': '说穿了，以艺术为创意的绘画，AI绘画根本就代替不了人工。”', 'colorStyle': 0, 'type': 1, 'createTime': 1731472675, 'refMpReviewId': 'MP_WXS_3079395914_zwAP0a86vIEXr8JF0zgYoQ'}, {'bookId': 'MP_WXS_3079395914', 'style': 0, 'bookmarkId': 'MP_WXS_3079395914_zwAP0a86vIEXr8JF0zgYoQ_1811-1857', 'bookVersion': 1731457718, 'range': '1811-1857', 'markText': '“在AI的助力下，推新周期在缩短，成本在降低，库存压力在下降，柔性供应链正在变得更加敏捷。”', 'colorStyle': 0, 'type': 1, 'createTime': 1731472647, 'refMpReviewId': 'MP_WXS_3079395914_zwAP0a86vIEXr8JF0zgYoQ'}, {'bookId': 'MP_WXS_3079395914', 'style': 0, 'bookmarkId': 'MP_WXS_3079395914_zwAP0a86vIEXr8JF0zgYoQ_1218-1327', 'bookVersion': 1731457718, 'range': '1218-1327', 'markText': '在跨境电商领域，商户们常用平台提供的AI翻译官、AI商品管理等服务。有商家表示：“只需要拍一段中文视频，上传到平台，视频就能自动被转换成36国语言，声音、口型都一致，完全看不出来是AI做的，订单量因此增长超过10%。”', 'colorStyle': 0, 'type': 1, 'createTime': 1731472595, 'refMpReviewId': 'MP_WXS_3079395914_zwAP0a86vIEXr8JF0zgYoQ'}, {'bookId': 'MP_WXS_3079395914', 'style': 0, 'bookmarkId': 'MP_WXS_3079395914_zwAP0a86vIEXr8JF0zgYoQ_1097-1216', 'bookVersion': 1731457718, 'range': '1097-1216', 'markText': '“比如我卖内衣，我们的技术，只需要商家把产品图片发过来，我们把内衣穿在假人模特商训练好，就能用AI生成模特试穿图，非常真实，表情自然，不存在版权问题。本来模特要钱，尤其是内衣模特价格昂贵，摄影师也要钱，人工成本非常高，现在都可以省掉了。”', 'colorStyle': 0, 'type': 1, 'createTime': 1731472562, 'refMpReviewId': 'MP_WXS_3079395914_zwAP0a86vIEXr8JF0zgYoQ'}, {'bookId': 'MP_WXS_3079395914', 'style': 0, 'bookmarkId': 'MP_WXS_3079395914_zwAP0a86vIEXr8JF0zgYoQ_364-398', 'bookVersion': 1731457718, 'range': '364-398', 'markText': '在抖音，2000元一个月的AI主播为商家节省了不少搭建直播间的成本。', 'colorStyle': 0, 'type': 1, 'createTime': 1731472500, 'refMpReviewId': 'MP_WXS_3079395914_zwAP0a86vIEXr8JF0zgYoQ'}, {'bookId': 'MP_WXS_3079395914', 'style': 0, 'bookmarkId': 'MP_WXS_3079395914_zwAP0a86vIEXr8JF0zgYoQ_222-250', 'bookVersion': 1731457718, 'range': '222-250', 'markText': '除了搜索，电商已是当下公认的AI商业化落地最普遍的场景。', 'colorStyle': 0, 'type': 1, 'createTime': 1731472477, 'refMpReviewId': 'MP_WXS_3079395914_zwAP0a86vIEXr8JF0zgYoQ'}, {'bookId': 'MP_WXS_3079395914', 'style': 0, 'bookmarkId': 'MP_WXS_3079395914_iS5gNSIGmEvXiES2WcDw8w_4135-4186', 'bookVersion': 1730940724, 'range': '4135-4186', 'markText': '针对整体冲击，有“将进一步倒逼中国加速扩容内需消费市场，出台更激进的投资刺激政策，加速产业转型”等等。', 'colorStyle': 0, 'type': 1, 'createTime': 1730954164, 'refMpReviewId': 'MP_WXS_3079395914_iS5gNSIGmEvXiES2WcDw8w'}, {'bookId': 'MP_WXS_3079395914', 'style': 0, 'bookmarkId': 'MP_WXS_3079395914_iS5gNSIGmEvXiES2WcDw8w_3456-3480', 'bookVersion': 1730940724, 'range': '3456-3480', 'markText': '第五，加关税引发强美元预期，进而冲击人民币汇率。', 'colorStyle': 0, 'type': 1, 'createTime': 1730954075, 'refMpReviewId': 'MP_WXS_3079395914_iS5gNSIGmEvXiES2WcDw8w'}, {'bookId': 'MP_WXS_3079395914', 'style': 0, 'bookmarkId': 'MP_WXS_3079395914_iS5gNSIGmEvXiES2WcDw8w_3392-3443', 'bookVersion': 1730940724, 'range': '3392-3443', 'markText': '第四，移民限制和人员流动限制。截至今年9月，2024年中美之间的航班量才恢复至2019年26%的水平。', 'colorStyle': 0, 'type': 1, 'createTime': 1730954054, 'refMpReviewId': 'MP_WXS_3079395914_iS5gNSIGmEvXiES2WcDw8w'}, {'bookId': 'MP_WXS_3079395914', 'style': 0, 'bookmarkId': 'MP_WXS_3079395914_iS5gNSIGmEvXiES2WcDw8w_3281-3388', 'bookVersion': 1730940724, 'range': '3281-3388', 'markText': '第三，是投资限制，比如禁止中国资本投资美国尤其是高科技行业；限制中国人购买资产等。2016年，中国企业在美国的投资达到了惊人的480亿美元；2022年这一数字萎缩到只有31亿美元。与此同时，也限制美国对中国的投资。', 'colorStyle': 0, 'type': 1, 'createTime': 1730954041, 'refMpReviewId': 'MP_WXS_3079395914_iS5gNSIGmEvXiES2WcDw8w'}, {'bookId': 'MP_WXS_3079395914', 'style': 0, 'bookmarkId': 'MP_WXS_3079395914_iS5gNSIGmEvXiES2WcDw8w_3215-3234', 'bookVersion': 1730940724, 'range': '3215-3234', 'markText': '第二，比贸易摩擦更确定的，是科技摩擦。', 'colorStyle': 0, 'type': 1, 'createTime': 1730954027, 'refMpReviewId': 'MP_WXS_3079395914_iS5gNSIGmEvXiES2WcDw8w'}, {'bookId': 'MP_WXS_3079395914', 'style': 0, 'bookmarkId': 'MP_WXS_3079395914_iS5gNSIGmEvXiES2WcDw8w_3050-3179', 'bookVersion': 1730940724, 'range': '3050-3179', 'markText': '首先，麻烦来自特朗普主义中的“经济民粹主义”。贸易首当其冲，“关税”大棒几乎确定会加码。这一领域也是特朗普2016年任期内，唯一一个100%达成的竞选承诺。\n\n如今，按照本次竞选期间的口号，将对中国商品征收60%关税，且会限制中国通过第三国对美国的间接出口。', 'colorStyle': 0, 'type': 1, 'createTime': 1730953997, 'refMpReviewId': 'MP_WXS_3079395914_iS5gNSIGmEvXiES2WcDw8w'}, {'bookId': 'MP_WXS_3079395914', 'style': 0, 'bookmarkId': 'MP_WXS_3079395914_iS5gNSIGmEvXiES2WcDw8w_2224-2368', 'bookVersion': 1730940724, 'range': '2224-2368', 'markText': '只是近几年来，民主党在反垄断、数据隐私保护监管方面加大了力度，引起了硅谷的不满，同时又出于对“极端政治正确”的担忧，以及经不住特朗普减税政策、创新保护的诱惑，一大批科技精英转投共和党。\n\n最具代表性的是比尔盖茨和马斯克，一位投资了哈里斯5000多万美元，一位先后投入超过1亿美元支持特朗普', 'colorStyle': 0, 'type': 1, 'createTime': 1730953920, 'refMpReviewId': 'MP_WXS_3079395914_iS5gNSIGmEvXiES2WcDw8w'}, {'bookId': 'MP_WXS_3079395914', 'style': 0, 'bookmarkId': 'MP_WXS_3079395914_iS5gNSIGmEvXiES2WcDw8w_2126-2222', 'bookVersion': 1730940724, 'range': '2126-2222', 'markText': '其次是科技圈和精英圈的撕裂。主流硅谷科技精英向来倾向于民主党，他们认为自己的价值观更具“进步性”，所接受的教育也包含多元文化和社会正义的理念，而民主党对移民、公共教育、科研投入等支持程度较高。', 'colorStyle': 0, 'type': 1, 'createTime': 1730953881, 'refMpReviewId': 'MP_WXS_3079395914_iS5gNSIGmEvXiES2WcDw8w'}, {'bookId': 'MP_WXS_3079395914', 'style': 0, 'bookmarkId': 'MP_WXS_3079395914_iS5gNSIGmEvXiES2WcDw8w_1813-1986', 'bookVersion': 1730940724, 'range': '1813-1986', 'markText': '民主党将MAGA称为“Dark MAGA”，认为一个接近于法西斯的政治流氓再次上台，将摧毁美国一切美好的制度，美国到了绝望的至暗时刻；而MAGA却认为这是反抗和凯旋的旗帜。多元文化的拥趸已理所应当地将“结果正义”等同于原本的“机会正义”，造成了社会出现新的不公平。\n\n总而言之，这越来越像是一种基于宗教般的社会身份认同感，而非基于实际政策的分歧。', 'colorStyle': 0, 'type': 1, 'createTime': 1730953783, 'refMpReviewId': 'MP_WXS_3079395914_iS5gNSIGmEvXiES2WcDw8w'}, {'bookId': 'MP_WXS_3079395914', 'style': 0, 'bookmarkId': 'MP_WXS_3079395914_iS5gNSIGmEvXiES2WcDw8w_862-969', 'bookVersion': 1730940724, 'range': '862-969', 'markText': '号令“一府两院”后，特朗普就可以在最高法院大法官等关键人选的任命上拥有绝对的话语权，让共和党的支持者成为终身大法官。就算不换人，最高法院中也有6名偏向共和党的保守派大法官，他们皆由特朗普在上一次担任总统时亲自任命。', 'colorStyle': 0, 'type': 1, 'createTime': 1730953628, 'refMpReviewId': 'MP_WXS_3079395914_iS5gNSIGmEvXiES2WcDw8w'}, {'bookId': 'MP_WXS_3079395914', 'style': 0, 'bookmarkId': 'MP_WXS_3079395914_iS5gNSIGmEvXiES2WcDw8w_826-860', 'bookVersion': 1730940724, 'range': '826-860', 'markText': '如果顺利拿下众议院，美国将形成“一府两院”都由共和党掌控的强势局面。', 'colorStyle': 0, 'type': 1, 'createTime': 1730953611, 'refMpReviewId': 'MP_WXS_3079395914_iS5gNSIGmEvXiES2WcDw8w'}, {'bookId': 'MP_WXS_3079395914', 'style': 0, 'bookmarkId': 'MP_WXS_3079395914_iS5gNSIGmEvXiES2WcDw8w_434-520', 'bookVersion': 1730940724, 'range': '434-520', 'markText': '美国宪法规定，美国政府的结构按照“三权分立”原则，仅有行政权归总统，总统组建的内阁中有1位副总统，15位部长，及其他内阁级官员。在此之外，则是立法权和司法权制约总统的权力。', 'colorStyle': 0, 'type': 1, 'createTime': 1730953496, 'refMpReviewId': 'MP_WXS_3079395914_iS5gNSIGmEvXiES2WcDw8w'}, {'bookId': 'MP_WXS_3079395914', 'style': 0, 'bookmarkId': 'MP_WXS_3079395914_iS5gNSIGmEvXiES2WcDw8w_223-257', 'bookVersion': 1730940724, 'range': '223-257', 'markText': '他迟早会去的，但却是王者归来，成为美国历史上第二位非连续当选的总统。', 'colorStyle': 0, 'type': 1, 'createTime': 1730953453, 'refMpReviewId': 'MP_WXS_3079395914_iS5gNSIGmEvXiES2WcDw8w'}, {'bookId': 'MP_WXS_3079395914', 'style': 0, 'bookmarkId': 'MP_WXS_3079395914_iS5gNSIGmEvXiES2WcDw8w_134-169', 'bookVersion': 1730940724, 'range': '134-169', 'markText': '宾夕法尼亚的子弹没有带走特朗普，反而送了他19张珍贵的摇摆州选举人票。', 'colorStyle': 0, 'type': 1, 'createTime': 1730953438, 'refMpReviewId': 'MP_WXS_3079395914_iS5gNSIGmEvXiES2WcDw8w'}, {'bookId': 'MP_WXS_3079395914', 'style': 0, 'bookmarkId': 'MP_WXS_3079395914_DJm0tuO77ujroYIyl5zLpw_4674-4718', 'bookVersion': 1730680453, 'range': '4674-4718', 'markText': '六大世界马拉松大满贯赛事之一的波士顿马拉松，其在1897年举办，仅比第一届奥运会晚一年。', 'colorStyle': 0, 'type': 1, 'createTime': 1730717157, 'refMpReviewId': 'MP_WXS_3079395914_DJm0tuO77ujroYIyl5zLpw'}, {'bookId': 'MP_WXS_3079395914', 'style': 0, 'bookmarkId': 'MP_WXS_3079395914_DJm0tuO77ujroYIyl5zLpw_3617-3684', 'bookVersion': 1730680453, 'range': '3617-3684', 'markText': '一场比赛主要的运营成本包括赛事运营授权费、电视转播费、安保费和人力成本等，不同城市的不同规模赛事的辐射影响力，会显著影响赛事授权价格。', 'colorStyle': 0, 'type': 1, 'createTime': 1730717005, 'refMpReviewId': 'MP_WXS_3079395914_DJm0tuO77ujroYIyl5zLpw'}, {'bookId': 'MP_WXS_3079395914', 'style': 0, 'bookmarkId': 'MP_WXS_3079395914_DJm0tuO77ujroYIyl5zLpw_3080-3112', 'bookVersion': 1730680453, 'range': '3080-3112', 'markText': '更大的赢家，则是政府。毕竟政府对赛事补贴，本质也是因为有利可图。', 'colorStyle': 0, 'type': 1, 'createTime': 1730716980, 'refMpReviewId': 'MP_WXS_3079395914_DJm0tuO77ujroYIyl5zLpw'}, {'bookId': 'MP_WXS_3079395914', 'style': 0, 'bookmarkId': 'MP_WXS_3079395914_DJm0tuO77ujroYIyl5zLpw_3244-3338', 'bookVersion': 1730680453, 'range': '3244-3338', 'markText': '来自第三方评估机构的数据显示，来兰参赛的外地选手平均在兰州停留时间为3天，平均携带亲友3.66人，本次赛事领物人数为38116人，外地选手比例达61.15%，本地选手比例达38.85%。\n', 'colorStyle': 0, 'type': 1, 'createTime': 1730716968, 'refMpReviewId': 'MP_WXS_3079395914_DJm0tuO77ujroYIyl5zLpw'}, {'bookId': 'MP_WXS_3079395914', 'style': 0, 'bookmarkId': 'MP_WXS_3079395914_DJm0tuO77ujroYIyl5zLpw_3432-3458', 'bookVersion': 1730680453, 'range': '3432-3458', 'markText': '除了经济效益外，马拉松还能产生溢出效益，拉动旅游业。', 'colorStyle': 0, 'type': 1, 'createTime': 1730716959, 'refMpReviewId': 'MP_WXS_3079395914_DJm0tuO77ujroYIyl5zLpw'}, {'bookId': 'MP_WXS_3079395914', 'style': 0, 'bookmarkId': 'MP_WXS_3079395914_DJm0tuO77ujroYIyl5zLpw_2756-2806', 'bookVersion': 1730680453, 'range': '2756-2806', 'markText': '据前瞻产业研究院数据，一般当地政府对马拉松的补贴约为100-200万元，国际赛事最高补贴300万元。', 'colorStyle': 0, 'type': 1, 'createTime': 1730716900, 'refMpReviewId': 'MP_WXS_3079395914_DJm0tuO77ujroYIyl5zLpw'}, {'bookId': 'MP_WXS_3079395914', 'style': 0, 'bookmarkId': 'MP_WXS_3079395914_DJm0tuO77ujroYIyl5zLpw_2311-2441', 'bookVersion': 1730680453, 'range': '2311-2441', 'markText': '赞助马拉松赛事的，一开始只有冠名赞助商、官方合作伙伴、赞助商和供应商四个分类。\n\n2024年的无锡马拉松，又多出了顶级合作伙伴、专项服务商和官方合作酒店四个分类，如上海马拉松，又会多出物流服务商、保险服务商、官方指定能量胶合作商和官方指定摄影服务商等各种分类。', 'colorStyle': 0, 'type': 1, 'createTime': 1730716861, 'refMpReviewId': 'MP_WXS_3079395914_DJm0tuO77ujroYIyl5zLpw'}, {'bookId': 'MP_WXS_3079395914', 'style': 0, 'bookmarkId': 'MP_WXS_3079395914_DJm0tuO77ujroYIyl5zLpw_2224-2293', 'bookVersion': 1730680453, 'range': '2224-2293', 'markText': '目前国内一二线城市的马拉松赛事，参与人数大多在2—5万人之间，报名费也在100—200元左右，算下来报名费基本在200—1000万元不等。', 'colorStyle': 0, 'type': 1, 'createTime': 1730716844, 'refMpReviewId': 'MP_WXS_3079395914_DJm0tuO77ujroYIyl5zLpw'}, {'bookId': 'MP_WXS_3079395914', 'style': 0, 'bookmarkId': 'MP_WXS_3079395914_DJm0tuO77ujroYIyl5zLpw_2443-2530', 'bookVersion': 1730680453, 'range': '2443-2530', 'markText': '算下来，一场马拉松至少有超过十家赞助商。有专家算过，���般冠名商的赞助费千万起步，合作伙伴则需付出500—800万元，赞助商的费用通常是两三百万元，供应商百万级别就可以挤进来。', 'colorStyle': 0, 'type': 1, 'createTime': 1730716835, 'refMpReviewId': 'MP_WXS_3079395914_DJm0tuO77ujroYIyl5zLpw'}, {'bookId': 'MP_WXS_3079395914', 'style': 0, 'bookmarkId': 'MP_WXS_3079395914_DJm0tuO77ujroYIyl5zLpw_1877-1918', 'bookVersion': 1730680453, 'range': '1877-1918', 'markText': '所以业内还有句话来形容爱跑马拉松的人群——“三高人群”，即高收入、高学历、高职位。', 'colorStyle': 0, 'type': 1, 'createTime': 1730716777, 'refMpReviewId': 'MP_WXS_3079395914_DJm0tuO77ujroYIyl5zLpw'}, {'bookId': 'MP_WXS_3079395914', 'style': 0, 'bookmarkId': 'MP_WXS_3079395914_DJm0tuO77ujroYIyl5zLpw_1743-1874', 'bookVersion': 1730680453, 'range': '1743-1874', 'markText': '而根据果动科技的《2023中国跑路赛事蓝皮书》数据，去年公路长跑赛事的参赛选手，机关事业单位员工、企业管理者的人群占比达到32.13%，本科及以上学历占比高达61.17%，购买运动防护用品消费总支出超过2000元的，占比达30.21%，30岁到50岁的人群居多。', 'colorStyle': 0, 'type': 1, 'createTime': 1730716771, 'refMpReviewId': 'MP_WXS_3079395914_DJm0tuO77ujroYIyl5zLpw'}, {'bookId': 'MP_WXS_3079395914', 'style': 0, 'bookmarkId': 'MP_WXS_3079395914_DJm0tuO77ujroYIyl5zLpw_871-956', 'bookVersion': 1730680453, 'range': '871-956', 'markText': '但国内马拉松进入爆发期的真正出现转折点，是在2010年后的政策推动。\n\n2013年，国务院印发了《关于加快发展体育产业促进体育消费的若干意见》，把全民健身上升为国家战略。', 'colorStyle': 0, 'type': 1, 'createTime': 1730716704, 'refMpReviewId': 'MP_WXS_3079395914_DJm0tuO77ujroYIyl5zLpw'}, {'bookId': 'MP_WXS_3079395914', 'style': 0, 'bookmarkId': 'MP_WXS_3079395914_DJm0tuO77ujroYIyl5zLpw_444-537', 'bookVersion': 1730680453, 'range': '444-537', 'markText': '在地球的另一端，美国的纽约马拉松、波士顿马拉松等多个马拉松赛事都在同一天鸣枪开赛，同样吸引了数万人参赛。\n\n究其原因，一方面是季节因素，每年3月份和11月份是一年当中跑马拉松的黄金时段。', 'colorStyle': 0, 'type': 1, 'createTime': 1730716636, 'refMpReviewId': 'MP_WXS_3079395914_DJm0tuO77ujroYIyl5zLpw'}, {'bookId': 'MP_WXS_3079395914', 'style': 0, 'bookmarkId': 'MP_WXS_3079395914_DJm0tuO77ujroYIyl5zLpw_61-111', 'bookVersion': 1730680453, 'range': '61-111', 'markText': '当一个国家的人均GDP超过5000美元并不断提高时，会进入以马拉松为代表的全民公路长跑体育消费周期。', 'colorStyle': 0, 'type': 1, 'createTime': 1730716622, 'refMpReviewId': 'MP_WXS_3079395914_DJm0tuO77ujroYIyl5zLpw'}, {'bookId': 'MP_WXS_3079395914', 'style': 0, 'bookmarkId': 'MP_WXS_3079395914_DJm0tuO77ujroYIyl5zLpw_309-378', 'bookVersion': 1730680453, 'range': '309-378', 'markText': '11月3日当天，北京马拉松赛、杭州马拉松赛、郑州马拉松赛、宜昌马拉松赛、西安马拉松赛、漠河北极村马拉松赛等纷纷在近十个城市和地区鸣枪举办。', 'colorStyle': 0, 'type': 1, 'createTime': 1730716612, 'refMpReviewId': 'MP_WXS_3079395914_DJm0tuO77ujroYIyl5zLpw'}, {'bookId': 'MP_WXS_3079395914', 'style': 0, 'bookmarkId': 'MP_WXS_3079395914_9B4J96Jkv1~sjbCl~AdoKg_4081-4097', 'bookVersion': 1730217656, 'range': '4081-4097', 'markText': '涓涓细流汇成海，点点纤尘积就山。', 'colorStyle': 0, 'type': 1, 'createTime': 1730263504, 'refMpReviewId': 'MP_WXS_3079395914_9B4J96Jkv1~sjbCl~AdoKg'}, {'bookId': 'MP_WXS_3079395914', 'style': 0, 'bookmarkId': 'MP_WXS_3079395914_9B4J96Jkv1~sjbCl~AdoKg_3685-3724', 'bookVersion': 1730217656, 'range': '3685-3724', 'markText': '正如一位淄博烧烤店老板所言：“我们已经不再是为了赚钱，而是为淄博的荣誉而战。”', 'colorStyle': 0, 'type': 1, 'createTime': 1730263488, 'refMpReviewId': 'MP_WXS_3079395914_9B4J96Jkv1~sjbCl~AdoKg'}, {'bookId': 'MP_WXS_3079395914', 'style': 0, 'bookmarkId': 'MP_WXS_3079395914_9B4J96Jkv1~sjbCl~AdoKg_3525-3595', 'bookVersion': 1730217656, 'range': '3525-3595', 'markText': '淄博市委市政府成立了工作专班，适时推出“烧烤专列”、新增烧烤公交专线、修建八大局停车场、发布烧烤地图、大量修建“放心亭”，大大提升游玩体验。', 'colorStyle': 0, 'type': 1, 'createTime': 1730263475, 'refMpReviewId': 'MP_WXS_3079395914_9B4J96Jkv1~sjbCl~AdoKg'}, {'bookId': 'MP_WXS_3079395914', 'style': 0, 'bookmarkId': 'MP_WXS_3079395914_9B4J96Jkv1~sjbCl~AdoKg_3455-3522', 'bookVersion': 1730217656, 'range': '3455-3522', 'markText': '全国主打烧烤美食的城市那么多，为什么只有淄博能持续火热？因为400多万淄博人都憋着一股劲，要做好自己的本职工作，给游客提供超预期的服务', 'colorStyle': 0, 'type': 1, 'createTime': 1730263459, 'refMpReviewId': 'MP_WXS_3079395914_9B4J96Jkv1~sjbCl~AdoKg'}, {'bookId': 'MP_WXS_3079395914', 'style': 0, 'bookmarkId': 'MP_WXS_3079395914_9B4J96Jkv1~sjbCl~AdoKg_2894-2955', 'bookVersion': 1730217656, 'range': '2894-2955', 'markText': '原产于北大西洋的鲑鱼，被日照市岚山区大量引进。该地计划打造全国最大的三文鱼苗种繁育中心和全国首个三文鱼全产业链发展示范区。', 'colorStyle': 0, 'type': 1, 'createTime': 1730263443, 'refMpReviewId': 'MP_WXS_3079395914_9B4J96Jkv1~sjbCl~AdoKg'}, {'bookId': 'MP_WXS_3079395914', 'style': 0, 'bookmarkId': 'MP_WXS_3079395914_9B4J96Jkv1~sjbCl~AdoKg_2774-2814', 'bookVersion': 1730217656, 'range': '2774-2814', 'markText': '山东小县城还擅长“无中生有”，把海外“舶来品”做成“土特产”，然后销往全球市场。', 'colorStyle': 0, 'type': 1, 'createTime': 1730263436, 'refMpReviewId': 'MP_WXS_3079395914_9B4J96Jkv1~sjbCl~AdoKg'}, {'bookId': 'MP_WXS_3079395914', 'style': 0, 'bookmarkId': 'MP_WXS_3079395914_9B4J96Jkv1~sjbCl~AdoKg_2816-2892', 'bookVersion': 1730217656, 'range': '2816-2892', 'markText': '原产于法国的朗德鹅，如今是潍坊市临朐县的一张名片。2023年，临朐县出栏朗德鹅达500万只，加工鹅肝5000余吨，占全国产量的70%、全球市场的20%。', 'colorStyle': 0, 'type': 1, 'createTime': 1730263431, 'refMpReviewId': 'MP_WXS_3079395914_9B4J96Jkv1~sjbCl~AdoKg'}, {'bookId': 'MP_WXS_3079395914', 'style': 0, 'bookmarkId': 'MP_WXS_3079395914_9B4J96Jkv1~sjbCl~AdoKg_2576-2673', 'bookVersion': 1730217656, 'range': '2576-2673', 'markText': '在丁楼村的带动下，大集镇乃至曹县都走向了电商致富路。在阿里研究院发布的《2020年淘宝百强县名单》中，曹县以17个淘宝镇、151个淘宝村的数量位列全国第二，也是仅次于义乌的全国第二大淘宝村集群。', 'colorStyle': 0, 'type': 1, 'createTime': 1730263415, 'refMpReviewId': 'MP_WXS_3079395914_9B4J96Jkv1~sjbCl~AdoKg'}, {'bookId': 'MP_WXS_3079395914', 'style': 0, 'bookmarkId': 'MP_WXS_3079395914_9B4J96Jkv1~sjbCl~AdoKg_2104-2210', 'bookVersion': 1730217656, 'range': '2104-2210', 'markText': '位于鲁西南的曹县，原本是“光棍多、老人多、留守儿童多”的劳务输出县、贫困县，却通过抓住经济全球化和贸易数字化风口，成为全国闻名的产业大县：全国最大的演出服和汉服基地、全国最大桐木加工基地、日本棺木的主要生产基地。', 'colorStyle': 0, 'type': 1, 'createTime': 1730263373, 'refMpReviewId': 'MP_WXS_3079395914_9B4J96Jkv1~sjbCl~AdoKg'}, {'bookId': 'MP_WXS_3079395914', 'style': 0, 'bookmarkId': 'MP_WXS_3079395914_9B4J96Jkv1~sjbCl~AdoKg_1908-2016', 'bookVersion': 1730217656, 'range': '1908-2016', 'markText': '招远黄金占到了全国探明储量的八分之一，诸城拥有全球最大的经济型商用车制造基地，平度白色家电产量约占全国总量8%，青州是全国最大的盆栽花产业中心，广饶拥有全球单厂规模最大的新闻纸生产基地，莱州花岗岩总储量占全国10%。', 'colorStyle': 0, 'type': 1, 'createTime': 1730263353, 'refMpReviewId': 'MP_WXS_3079395914_9B4J96Jkv1~sjbCl~AdoKg'}, {'bookId': 'MP_WXS_3079395914', 'style': 0, 'bookmarkId': 'MP_WXS_3079395914_9B4J96Jkv1~sjbCl~AdoKg_1840-1906', 'bookVersion': 1730217656, 'range': '1840-1906', 'markText': '这12个县的经济实力，超过了西部地区很多地级市。龙口市、胶州市、滕州市、荣成市、寿光市、邹城市，2023年的GDP都超过了一千亿元。', 'colorStyle': 0, 'type': 1, 'createTime': 1730263330, 'refMpReviewId': 'MP_WXS_3079395914_9B4J96Jkv1~sjbCl~AdoKg'}, {'bookId': 'MP_WXS_3079395914', 'style': 0, 'bookmarkId': 'MP_WXS_3079395914_9B4J96Jkv1~sjbCl~AdoKg_1361-1403', 'bookVersion': 1730217656, 'range': '1361-1403', 'markText': '任晓猛夫妻的油条生意越做越大，打造出了连锁品牌“油条任家”，全国有100多家加盟店。', 'colorStyle': 0, 'type': 1, 'createTime': 1730263295, 'refMpReviewId': 'MP_WXS_3079395914_9B4J96Jkv1~sjbCl~AdoKg'}, {'bookId': 'MP_WXS_3079395914', 'style': 0, 'bookmarkId': 'MP_WXS_3079395914_9B4J96Jkv1~sjbCl~AdoKg_989-1070', 'bookVersion': 1730217656, 'range': '989-1070', 'markText': '截至2024年4月底，山东实有经营主体1478.82万户，居全国第二位。而以山东省2023年末常住人口10123万为准，粗略计算，“每七个山东人，就有一个老板”。', 'colorStyle': 0, 'type': 1, 'createTime': 1730263258, 'refMpReviewId': 'MP_WXS_3079395914_9B4J96Jkv1~sjbCl~AdoKg'}, {'bookId': 'MP_WXS_3079395914', 'style': 0, 'bookmarkId': 'MP_WXS_3079395914_9B4J96Jkv1~sjbCl~AdoKg_936-987', 'bookVersion': 1730217656, 'range': '936-987', 'markText': '不过，家业再大的省份，也是由无数个经济细胞组成的。山东的经济活力，恰恰体现在小老板、小县城和小城市上。', 'colorStyle': 0, 'type': 1, 'createTime': 1730263244, 'refMpReviewId': 'MP_WXS_3079395914_9B4J96Jkv1~sjbCl~AdoKg'}, {'bookId': 'MP_WXS_3079395914', 'style': 0, 'bookmarkId': 'MP_WXS_3079395914_9B4J96Jkv1~sjbCl~AdoKg_886-934', 'bookVersion': 1730217656, 'range': '886-934', 'markText': '山东的经济体量大，仅次于广东、江苏，排全国第三。山东的农业规模大，农林牧渔业总产值稳居全国首位。', 'colorStyle': 0, 'type': 1, 'createTime': 1730263238, 'refMpReviewId': 'MP_WXS_3079395914_9B4J96Jkv1~sjbCl~AdoKg'}, {'bookId': 'MP_WXS_3079395914', 'style': 0, 'bookmarkId': 'MP_WXS_3079395914_9B4J96Jkv1~sjbCl~AdoKg_583-655', 'bookVersion': 1730217656, 'range': '583-655', 'markText': '除了《问政山东》外，山东这几年还贡献了“宇宙中心曹县”“淄博烧烤”“山东文旅喊麦”“菏泽南站郭有才”“山东车牌之歌”“泰山专治嘴硬”等热搜词条。', 'colorStyle': 0, 'type': 1, 'createTime': 1730263190, 'refMpReviewId': 'MP_WXS_3079395914_9B4J96Jkv1~sjbCl~AdoKg'}], 'removed': [], 'chapters': [], 'book': {'bookId': 'MP_WXS_3079395914', 'version': 0, 'format': 'epub', 'soldout': 0, 'bookStatus': 2, 'cover': 'http://rescdn.qqmail.com/weread/cover/0/0/t8_0.jpg', 'title': '吴晓波频道', 'author': '公众号', 'coverBoxInfo': {}}, 'refMpInfos': [{'reviewId': 'MP_WXS_3079395914_9B4J96Jkv1~sjbCl~AdoKg', 'title': '《问政山东》里的另一个山东', 'pic_url': 'https://mmbiz.qpic.cn/mmbiz_jpg/pmBoItic0ByhBcQHvseoRRRDw4icEbovmZbg1GHXzJgngREXUgZJe0c5gaFYXWBmmEQRlwzR2T0hEp5YmyMBhiaGg/0?wx_fmt=jpeg', 'createTime': 1730217656}, {'reviewId': 'MP_WXS_3079395914_zwAP0a86vIEXr8JF0zgYoQ', 'title': '这个双十一，用AI的卖家领先了么？', 'pic_url': 'https://mmbiz.qpic.cn/mmbiz_jpg/pmBoItic0BygyACqswiaxUQqeJshemQNQOea16JWLjExluLUAy1KTaia0BGv28mDOyO1TibjLsNONSibicv5n2EJSkPQ/0?wx_fmt=jpeg', 'createTime': 1731261500}, {'reviewId': 'MP_WXS_3079395914_SEa0M2gqib8-Rjxl73AAxw', 'title': '双11还是给了我们九个惊喜点', 'pic_url': 'https://mmbiz.qpic.cn/mmbiz_jpg/pmBoItic0ByjncMswQIhZPujWpbTDP44sVtzMhibPTj7q7NbRVeMURUjA8KuHyDvHgm9XIh4hJMSmp0A5CrNg3JA/0?wx_fmt=jpeg', 'createTime': 1731689635}, {'reviewId': 'MP_WXS_3079395914_iS5gNSIGmEvXiES2WcDw8w', 'title': '重新认识这位特朗普', 'pic_url': 'https://mmbiz.qpic.cn/mmbiz_jpg/pmBoItic0BygKd7aTFOcWJjCGgCpxlShHhx3pv7hfN143d0TdDf9NSVaXnrbo60KqsyOn0yMTU0Bb7AAhjUAia5A/0?wx_fmt=jpeg', 'createTime': 1730940724}, {'reviewId': 'MP_WXS_3079395914_LVUH7KAEQoZr1Ysig1dPXQ', 'title': '中国财政部为什么要发行“美债”？', 'pic_url': 'https://mmbiz.qpic.cn/mmbiz_jpg/pmBoItic0Byia6vQsGto7Suth8uMuceRdCGviabUOHviaUAP4ZI8PYsFU8uLlvv4gfq9em8xVje6CQJt0hJHBic3oqg/0?wx_fmt=jpeg', 'createTime': 1731602569}, {'reviewId': 'MP_WXS_3079395914_DJm0tuO77ujroYIyl5zLpw', 'title': '全国各地怎么这么多马拉松比赛？', 'pic_url': 'https://mmbiz.qpic.cn/mmbiz_jpg/pmBoItic0ByhuPSHvwbh7lJiaeoDv83qFFSclp4lk9HAraXY8yTJWd1ib7bqjiaeQuyy7OtxFiaic2KUmpPCYCUsO8Bg/0?wx_fmt=jpeg', 'createTime': 1730680453}, {'reviewId': 'MP_WXS_3079395914_O-ou-GeV4jWwNOwHPDQkZQ', 'title': '二手房拐点来了吗？', 'pic_url': 'https://mmbiz.qpic.cn/mmbiz_jpg/pmBoItic0Byjjtn3ljtwQm13SQhiaicsKgPz0nAAhcyOCyHjkcMwlvsX8L6fhibs4RSJEnMwVEzDwMMTQam5icEDWvw/0?wx_fmt=jpeg', 'createTime': 1731775599}]}
        # updated = r.json().get("updated")
        updated = sorted(
            updated,
            key=lambda x: (x.get("chapterUid", 1), int(x.get("range").split("-")[0])),
        )
        return result
    return None


def get_read_info(bookId):
    params = dict(bookId=bookId, readingDetail=1, readingBookIndex=1, finishedDate=1)
    r = session.get(WEREAD_READ_INFO_URL, params=params)
    if r.ok:
        return r.json()
    return None


def get_bookinfo(bookId):
    """获取书的详情"""
    params = dict(bookId=bookId)
    r = session.get(WEREAD_BOOK_INFO, params=params)
    isbn = ""
    if r.ok:
        data = r.json()
        # print(f"=={data}")
        # {'bookId': 'MP_WXS_3079395914', 'title': '吴晓波频道', 'author': '公众号', 'cover': 'http://wx.qlogo.cn/mmhead/Q3auHgzwzM5KnT1Dw5FnZyb1QlZJWPJUEYYavg1z6XebFibKQ6nV60g/0', 'version': 1731775599, 'format': 'epub', 'type': 3, 'price': 0, 'originalPrice': 0, 'soldout': 0, 'bookStatus': 2, 'payType': 32, 'intro': '这是财经作家吴晓波带领“巴九灵”们运营的知识平台，这里汇聚了400多万认可商业之美、崇尚自我奋斗、乐意奉献共享、拒绝屌丝文化的新中产。', 'centPrice': 0, 'finished': 0, 'free': 1, 'mcardDiscount': 0, 'ispub': 0, 'cpid': 0, 'publishTime': '', 'authorVids': '42880929', 'hasLecture': 0, 'lastChapterIdx': 0, 'paperBook': {'skuId': ''}, 'copyrightChapterUids': [], 'blockSaveImg': 0, 'language': 'zh', 'hideUpdateTime': False, 'isEPUBComics': 0, 'webBookControl': 0, 'selfProduceIncentive': False, 'payingStatus': 0, 'chapterSize': 0, 'updateTime': 1731775599, 'onTime': 1731811455, 'unitPrice': 0, 'marketType': 3, 'isbn': '', 'publisher': '', 'totalWords': 0, 'shouldHideTTS': 0, 'recommended': 0, 'lectureRecommended': 0, 'follow': 0, 'secret': 0, 'offline': 0, 'lectureOffline': 0, 'finishReading': 0, 'hideReview': 0, 'hideFriendMark': 0, 'blacked': 0, 'isAutoPay': 0, 'availables': 0, 'paid': 0, 'isChapterPaid': 0, 'showLectureButton': 1, 'wxtts': 1, 'ratingCount': 194, 'ratingDetail': {'one': 20, 'two': 5, 'three': 7, 'four': 9, 'five': 151, 'recent': 0}, 'newRating': 811, 'newRatingCount': 127, 'deepVRating': 0, 'newRatingDetail': {'good': 103, 'fair': 12, 'poor': 12, 'recent': 0, 'deepV': 0, 'myRating': '', 'title': ''}, 'ranklist': {}, 'coverBoxInfo': {}, 'shortTimeRead': {'active': 0}, 'AISummary': ''}
        isbn = data["isbn"]
        newRating = data["newRating"] / 1000
        return (isbn, newRating)
    else:
        print(f"get {bookId} book info failed")
        return ("", 0)


def get_review_list(bookId):
    """获取笔记"""
    params = dict(bookId=bookId, listType=11, mine=1, syncKey=0)
    r = session.get(WEREAD_REVIEW_LIST_URL, params=params)
    # print(f"--{r.json()}")
    # {'totalCount': 0, 'reviews': [], 'removed': [], 'atUsers': [], 'refUsers': [], 'columns': [], 'hasMore': 0}
    reviews = r.json().get("reviews")
    summary = list(filter(lambda x: x.get("review").get("type") == 4, reviews))
    reviews = list(filter(lambda x: x.get("review").get("type") == 1, reviews))
    reviews = list(map(lambda x: x.get("review"), reviews))
    reviews = list(map(lambda x: {**x, "markText": x.pop("content")}, reviews))
    return summary, reviews


def check(bookId):
    """检查是否已经插入过 如果已经插入了就删除"""
    time.sleep(0.3)
    filter = {"property": "BookId", "rich_text": {"equals": bookId}}
    response = client.databases.query(database_id=database_id, filter=filter)
    for result in response["results"]:
        time.sleep(0.3)
        client.blocks.delete(block_id=result["id"])


def get_chapter_info(bookId):
    """获取章节信息(公众号没有章节信息)"""
    body = {"bookIds": [bookId], "synckeys": [0], "teenmode": 0}
    r = session.post(WEREAD_CHAPTER_INFO, json=body)
    if (
        r.ok
        and "data" in r.json()
        and len(r.json()["data"]) == 1
        and "updated" in r.json()["data"][0]
    ):
        update = r.json()["data"][0]["updated"]
        return {item["chapterUid"]: item for item in update}
    return None


def insert_to_notion(bookName, bookId, cover, sort, author, isbn, rating, categories):
    """插入到notion"""
    time.sleep(0.3)
    if not cover or not cover.startswith("http"):
        cover = "https://www.notion.so/icons/book_gray.svg"
    parent = {"database_id": database_id, "type": "database_id"}
    properties = {
        "BookName": get_title(bookName),
        "BookId": get_rich_text(bookId),
        "ISBN": get_rich_text(isbn),
        "URL": get_url(
            f"https://weread.qq.com/web/reader/{calculate_book_str_id(bookId)}"
        ),
        "Author": get_rich_text(author),
        "Sort": get_number(sort),
        "Rating": get_number(rating),
        "Cover": get_file(cover),
    }
    if categories != None:
        properties["Categories"] = get_multi_select(categories)
    read_info = get_read_info(bookId=bookId)
    if read_info != None:
        markedStatus = read_info.get("markedStatus", 0)
        readingTime = read_info.get("readingTime", 0)
        readingProgress = read_info.get("readingProgress", 0)
        format_time = ""
        hour = readingTime // 3600
        if hour > 0:
            format_time += f"{hour}时"
        minutes = readingTime % 3600 // 60
        if minutes > 0:
            format_time += f"{minutes}分"
        properties["Status"] = get_select("读完" if markedStatus == 4 else "在读")
        properties["ReadingTime"] = get_rich_text(format_time)
        properties["Progress"] = get_number(readingProgress)
        if "finishedDate" in read_info:
            properties["Date"] = get_date(
                datetime.utcfromtimestamp(read_info.get("finishedDate")).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            )

    icon = get_icon(cover)
    # notion api 限制100个block
    response = client.pages.create(parent=parent, icon=icon,cover=icon, properties=properties)
    id = response["id"]
    return id


def add_children(id, children):
    results = []
    for i in range(0, len(children) // 100 + 1):
        time.sleep(0.3)
        response = client.blocks.children.append(
            block_id=id, children=children[i * 100 : (i + 1) * 100]
        )
        results.extend(response.get("results"))
    return results if len(results) == len(children) else None


def add_grandchild(grandchild, results):
    for key, value in grandchild.items():
        time.sleep(0.3)
        id = results[key].get("id")
        client.blocks.children.append(block_id=id, children=[value])


def get_notebooklist():
    """获取笔记本列表"""
    r = session.get(WEREAD_NOTEBOOKS_URL)
    if r.ok:
        data = r.json()
        # print(f"++{data}")
        # {'synckey': 1731849521, 'totalBookCount': 66, 'noBookReviewCount': 0, 'books': [{'bookId': 'MP_WXS_3079395914', 'book': {'bookId': 'MP_WXS_3079395914', 'title': '吴晓波频道', 'author': '公众号', 'cover': 'http://wx.qlogo.cn/mmhead/Q3auHgzwzM5KnT1Dw5FnZyb1QlZJWPJUEYYavg1z6XebFibKQ6nV60g/0', 'version': 1731775599, 'format': 'epub', 'type': 3, 'price': 0, 'originalPrice': 0, 'soldout': 0, 'bookStatus': 2, 'payType': 32, 'centPrice': 0, 'finished': 0, 'free': 1, 'mcardDiscount': 0, 'ispub': 0, 'cpid': 0, 'publishTime': '', 'authorVids': '42880929', 'hasLecture': 0, 'lastChapterIdx': 0, 'paperBook': {'skuId': ''}, 'copyrightChapterUids': [], 'blockSaveImg': 0, 'language': 'zh', 'hideUpdateTime': False, 'isEPUBComics': 0, 'webBookControl': 0, 'selfProduceIncentive': False}, 'reviewCount': 0, 'reviewLikeCount': 0, 'reviewCommentCount': 0, 'noteCount': 70, 'bookmarkCount': 0, 'sort': 1731849521}, {'bookId': 'MP_WXS_3095118559', 'book': {'bookId': 'MP_WXS_3095118559', 'title': '每日人物', 'author': '公众号', 'cover': 'http://wx.qlogo.cn/mmhead/Q3auHgzwzM58QTm9725FhhW1Qv6ElgiatvWM9o1ynKiakussMXO6JY8g/0', 'version': 1731815106, 'format': 'epub', 'type': 3, 'price': 0, 'originalPrice': 0, 'soldout': 0, 'bookStatus': 2, 'payType': 32, 'centPrice': 0, 'finished': 0, 'free': 1, 'mcardDiscount': 0, 'ispub': 0, 'cpid': 0, 'publishTime': '', 'hasLecture': 0, 'lastChapterIdx': 0, 'paperBook': {'skuId': ''}, 'copyrightChapterUids': [], 'blockSaveImg': 0, 'language': 'zh', 'hideUpdateTime': False, 'isEPUBComics': 0, 'webBookControl': 0, 'selfProduceIncentive': False}, 'reviewCount': 0, 'reviewLikeCount': 0, 'reviewCommentCount': 0, 'noteCount': 83, 'bookmarkCount': 0, 'sort': 1731812826}, {'bookId': 'MP_WXS_1791575621', 'book': {'bookId': 'MP_WXS_1791575621', 'title': '三联生活周刊', 'author': '公众号', 'cover': 'http://wx.qlogo.cn/mmhead/Q3auHgzwzM7pldgOabHbYP4CjRhBr7bAIoV3G6rTgNDm4vlj4WbLhA/0', 'version': 1731815429, 'format': 'epub', 'type': 3, 'price': 0, 'originalPrice': 0, 'soldout': 0, 'bookStatus': 2, 'payType': 32, 'centPrice': 0, 'finished': 0, 'free': 1, 'mcardDiscount': 0, 'ispub': 0, 'cpid': 0, 'publishTime': '', 'hasLecture': 0, 'lastChapterIdx': 0, 'paperBook': {'skuId': ''}, 'copyrightChapterUids': [], 'blockSaveImg': 0, 'language': 'zh', 'hideUpdateTime': False, 'isEPUBComics': 0, 'webBookControl': 0, 'selfProduceIncentive': False}, 'reviewCount': 0, 'reviewLikeCount': 0, 'reviewCommentCount': 0, 'noteCount': 42, 'bookmarkCount': 0, 'sort': 1731811555}, {'bookId': 'CB_4P25Kq5NsFSN6rj6swEJW94d', 'book': {'bookId': 'CB_4P25Kq5NsFSN6rj6swEJW94d', 'title': '四级单词', 'author': '', 'cover': 'https://weread-1258476243.file.myqcloud.com/app/assets/bookcover/book_cover_default_imported_04.png', 'version': 1364448097, 'format': 'epub', 'type': 0, 'price': 0, 'originalPrice': 0, 'soldout': 0, 'bookStatus': 1, 'payType': 33, 'centPrice': 0, 'finished': 1, 'free': 1, 'mcardDiscount': 0, 'ispub': 0, 'cpid': 0, 'publishTime': '', 'hasLecture': 0, 'lastChapterIdx': 2, 'paperBook': {'skuId': ''}, 'copyrightChapterUids': [], 'limitShareChat': 0, 'blockSaveImg': 0, 'language': 'zh-wr', 'hideUpdateTime': False, 'isEPUBComics': 0, 'webBookControl': 0, 'selfProduceIncentive': False}, 'reviewCount': 0, 'reviewLikeCount': 0, 'reviewCommentCount': 0, 'noteCount': 12, 'bookmarkCount': 0, 'sort': 1731773131}, {'bookId': 'MP_WXS_3076942461', 'book': {'bookId': 'MP_WXS_3076942461', 'title': '孤独图书馆', 'author': '公众号', 'cover': 'http://wx.qlogo.cn/mmhead/Q3auHgzwzM7pg66sfra7wPCtqJFGaq0ntrfFS7GTlvbcpVenTRS2zw/0', 'version': 1731378064, 'format': 'epub', 'type': 3, 'price': 0, 'originalPrice': 0, 'soldout': 0, 'bookStatus': 2, 'payType': 32, 'centPrice': 0, 'finished': 0, 'free': 1, 'mcardDiscount': 0, 'ispub': 0, 'cpid': 0, 'publishTime': '', 'hasLecture': 0, 'lastChapterIdx': 0, 'paperBook': {'skuId': ''}, 'copyrightChapterUids': [], 'blockSaveImg': 0, 'language': 'zh', 'hideUpdateTime': False, 'isEPUBComics': 0, 'webBookControl': 0, 'selfProduceIncentive': False}, 'reviewCount': 0, 'reviewLikeCount': 0, 'reviewCommentCount': 0, 'noteCount': 2, 'bookmarkCount': 0, 'sort': 1731767274}, {'bookId': 'MP_WXS_3089351720', 'book': {'bookId': 'MP_WXS_3089351720', 'title': '三联生活实验室', 'author': '公众号', 'cover': 'http://wx.qlogo.cn/mmhead/Q3auHgzwzM437aibPAMRmUv7LFOD2pfTjuB9FEQSoPt6o0CrzbPfIvw/0', 'version': 1731746897, 'format': 'epub', 'type': 3, 'price': 0, 'originalPrice': 0, 'soldout': 0, 'bookStatus': 2, 'payType': 32, 'centPrice': 0, 'finished': 0, 'free': 1, 'mcardDiscount': 0, 'ispub': 0, 'cpid': 0, 'publishTime': '', 'hasLecture': 0, 'lastChapterIdx': 0, 'paperBook': {'skuId': ''}, 'copyrightChapterUids': [], 'blockSaveImg': 0, 'language': 'zh', 'hideUpdateTime': False, 'isEPUBComics': 0, 'webBookControl': 0, 'selfProduceIncentive': False}, 'reviewCount': 0, 'reviewLikeCount': 0, 'reviewCommentCount': 0, 'noteCount': 66, 'bookmarkCount': 0, 'sort': 1731766726}, {'bookId': 'MP_WXS_1432156401', 'book': {'bookId': 'MP_WXS_1432156401', 'title': '虎嗅APP', 'author': '公众号', 'cover': 'http://wx.qlogo.cn/mmhead/Q3auHgzwzM7C9HhFFFnhtWDyWZ5NbqCYILXgjgIGLr7oSOkH9lVceg/0', 'version': 1731835870, 'format': 'epub', 'type': 3, 'price': 0, 'originalPrice': 0, 'soldout': 0, 'bookStatus': 2, 'payType': 32, 'centPrice': 0, 'finished': 0, 'free': 1, 'mcardDiscount': 0, 'ispub': 0, 'cpid': 0, 'publishTime': '', 'hasLecture': 0, 'lastChapterIdx': 0, 'paperBook': {'skuId': ''}, 'copyrightChapterUids': [], 'blockSaveImg': 0, 'language': 'zh', 'hideUpdateTime': False, 'isEPUBComics': 0, 'webBookControl': 0, 'selfProduceIncentive': False}, 'reviewCount': 0, 'reviewLikeCount': 0, 'reviewCommentCount': 0, 'noteCount': 146, 'bookmarkCount': 0, 'sort': 1731761427}, {'bookId': 'MP_WXS_2398045780', 'book': {'bookId': 'MP_WXS_2398045780', 'title': 'ONE文艺生活', 'author': '公众号', 'cover': 'http://wx.qlogo.cn/mmhead/Q3auHgzwzM7icvOfGjy7Fdmpj7s6RHgqoyNmqs4XuqyXQAVqxw4v3bw/0', 'version': 1731647195, 'format': 'epub', 'type': 3, 'price': 0, 'originalPrice': 0, 'soldout': 0, 'bookStatus': 2, 'payType': 32, 'centPrice': 0, 'finished': 0, 'free': 1, 'mcardDiscount': 0, 'ispub': 0, 'cpid': 0, 'publishTime': '', 'hasLecture': 0, 'lastChapterIdx': 0, 'paperBook': {'skuId': ''}, 'copyrightChapterUids': [], 'blockSaveImg': 0, 'language': 'zh', 'hideUpdateTime': False, 'isEPUBComics': 0, 'webBookControl': 0, 'selfProduceIncentive': False}, 'reviewCount': 0, 'reviewLikeCount': 0, 'reviewCommentCount': 0, 'noteCount': 2, 'bookmarkCount': 0, 'sort': 1731761208}, {'bookId': 'MP_WXS_3917653187', 'book': {'bookId': 'MP_WXS_3917653187', 'title': '大橘创业说', 'author': '公众号', 'cover': 'http://wx.qlogo.cn/mmhead/Mjzdia7evAzw1j9YY5yAQsSS2ZbxIeiaaT4nmRczWE50vSsQ1WdPanialXlMB5QYwhMs35dUdfskSA/0', 'version': 1731756844, 'format': 'epub', 'type': 3, 'price': 0, 'originalPrice': 0, 'soldout': 0, 'bookStatus': 2, 'payType': 32, 'centPrice': 0, 'finished': 0, 'free': 1, 'mcardDiscount': 0, 'ispub': 0, 'cpid': 0, 'publishTime': '', 'hasLecture': 0, 'lastChapterIdx': 0, 'paperBook': {'skuId': ''}, 'copyrightChapterUids': [], 'blockSaveImg': 0, 'language': 'zh', 'hideUpdateTime': False, 'isEPUBComics': 0, 'webBookControl': 0, 'selfProduceIncentive': False}, 'reviewCount': 0, 'reviewLikeCount': 0, 'reviewCommentCount': 0, 'noteCount': 3, 'bookmarkCount': 0, 'sort': 1731760540}, {'bookId': 'MP_WXS_2391159676', 'book': {'bookId': 'MP_WXS_2391159676', 'title': 'penddy', 'author': '公众号', 'cover': 'http://wx.qlogo.cn/mmhead/Q3auHgzwzM4GRO0v0EWThEdsa86fzTWhduw6SqlNF3CAjmyJdCbY2Q/0', 'version': 1731729313, 'format': 'epub', 'type': 3, 'price': 0, 'originalPrice': 0, 'soldout': 0, 'bookStatus': 2, 'payType': 32, 'centPrice': 0, 'finished': 0, 'free': 1, 'mcardDiscount': 0, 'ispub': 0, 'cpid': 0, 'publishTime': '', 'hasLecture': 0, 'lastChapterIdx': 0, 'paperBook': {'skuId': ''}, 'copyrightChapterUids': [], 'blockSaveImg': 0, 'language': 'zh', 'hideUpdateTime': False, 'isEPUBComics': 0, 'webBookControl': 0, 'selfProduceIncentive': False}, 'reviewCount': 0, 'reviewLikeCount': 0, 'reviewCommentCount': 0, 'noteCount': 1, 'bookmarkCount': 0, 'sort': 1731759294}, {'bookId': 'MP_WXS_2394295980', 'book': {'bookId': 'MP_WXS_2394295980', 'title': '逐阅', 'author': '公众号', 'cover': 'http://wx.qlogo.cn/mmhead/v6XbW38nFORtG59cWmo0BNpicHNib1eM1z9QhGKXEhHlynOGiccuhroWrn4mMwWE0fWPKmaSibXcLM4/0', 'version': 1731599104, 'format': 'epub', 'type': 3, 'price': 0, 'originalPrice': 0, 'soldout': 0, 'bookStatus': 2, 'payType': 32, 'centPrice': 0, 'finished': 0, 'free': 1, 'mcardDiscount': 0, 'ispub': 0, 'cpid': 0, 'publishTime': '', 'hasLecture': 0, 'lastChapterIdx': 0, 'paperBook': {'skuId': ''}, 'copyrightChapterUids': [], 'blockSaveImg': 0, 'language': 'zh', 'hideUpdateTime': False, 'isEPUBComics': 0, 'webBookControl': 0, 'selfProduceIncentive': False}, 'reviewCount': 0, 'reviewLikeCount': 0, 'reviewCommentCount': 0, 'noteCount': 3, 'bookmarkCount': 0, 'sort': 1731755681}, {'bookId': 'CB_CRU4iW4iIFSN6rj6sw8GS8Qy', 'book': {'bookId': 'CB_CRU4iW4iIFSN6rj6sw8GS8Qy', 'title': '高中词汇', 'author': '', 'cover': 'https://weread-1258476243.file.myqcloud.com/app/assets/bookcover/book_cover_default_imported_03.png', 'version': 986182117, 'format': 'epub', 'type': 0, 'price': 0, 'originalPrice': 0, 'soldout': 0, 'bookStatus': 1, 'payType': 33, 'centPrice': 0, 'finished': 1, 'free': 1, 'mcardDiscount': 0, 'ispub': 0, 'cpid': 0, 'publishTime': '', 'hasLecture': 0, 'lastChapterIdx': 4, 'paperBook': {'skuId': ''}, 'copyrightChapterUids': [], 'limitShareChat': 0, 'blockSaveImg': 0, 'language': 'zh-wr', 'hideUpdateTime': False, 'isEPUBComics': 0, 'webBookControl': 0, 'selfProduceIncentive': False}, 'reviewCount': 0, 'reviewLikeCount': 0, 'reviewCommentCount': 0, 'noteCount': 10, 'bookmarkCount': 0, 'sort': 1731749542}, {'bookId': 'MP_WXS_3003709201', 'book': {'bookId': 'MP_WXS_3003709201', 'title': '人格志', 'author': '公众号', 'cover': 'http://wx.qlogo.cn/mmhead/Q3auHgzwzM59Xq82afQ5JF0ib6pnk1aYWZBXMIbhbDp0MqMw8BXYkUw/0', 'version': 1731585517, 'format': 'epub', 'type': 3, 'price': 0, 'originalPrice': 0, 'soldout': 0, 'bookStatus': 2, 'payType': 32, 'centPrice': 0, 'finished': 0, 'free': 1, 'mcardDiscount': 0, 'ispub': 0, 'cpid': 0, 'publishTime': '', 'hasLecture': 0, 'lastChapterIdx': 0, 'paperBook': {'skuId': ''}, 'copyrightChapterUids': [], 'blockSaveImg': 0, 'language': 'zh', 'hideUpdateTime': False, 'isEPUBComics': 0, 'webBookControl': 0, 'selfProduceIncentive': False}, 'reviewCount': 0, 'reviewLikeCount': 0, 'reviewCommentCount': 0, 'noteCount': 9, 'bookmarkCount': 0, 'sort': 1731719442}, {'bookId': 'MP_WXS_2399112600', 'book': {'bookId': 'MP_WXS_2399112600', 'title': '经济观察报', 'author': '公众号', 'cover': 'http://wx.qlogo.cn/mmhead/Q3auHgzwzM7S7qPWFs4TuKJFp1Xf6ldhEWWGVDENVibEKfAhd6AKeMQ/0', 'version': 1731841919, 'format': 'epub', 'type': 3, 'price': 0, 'originalPrice': 0, 'soldout': 0, 'bookStatus': 2, 'payType': 32, 'centPrice': 0, 'finished': 0, 'free': 1, 'mcardDiscount': 0, 'ispub': 0, 'cpid': 0, 'publishTime': '', 'hasLecture': 0, 'lastChapterIdx': 0, 'paperBook': {'skuId': ''}, 'copyrightChapterUids': [], 'blockSaveImg': 0, 'language': 'zh', 'hideUpdateTime': False, 'isEPUBComics': 0, 'webBookControl': 0, 'selfProduceIncentive': False}, 'reviewCount': 0, 'reviewLikeCount': 0, 'reviewCommentCount': 0, 'noteCount': 16, 'bookmarkCount': 0, 'sort': 1731719367}, {'bookId': 'MP_WXS_2103095721', 'book': {'bookId': 'MP_WXS_2103095721', 'title': '人物', 'author': '公众号', 'cover': 'http://wx.qlogo.cn/mmhead/Q3auHgzwzM67Mp30XXLpu5jZnUZDPWPS5D7dN20EHGg3xMl0eicQGCw/0', 'version': 1731809046, 'format': 'epub', 'type': 3, 'price': 0, 'originalPrice': 0, 'soldout': 0, 'bookStatus': 2, 'payType': 32, 'centPrice': 0, 'finished': 0, 'free': 1, 'mcardDiscount': 0, 'ispub': 0, 'cpid': 0, 'publishTime': '', 'hasLecture': 0, 'lastChapterIdx': 0, 'paperBook': {'skuId': ''}, 'copyrightChapterUids': [], 'blockSaveImg': 0, 'language': 'zh', 'hideUpdateTime': False, 'isEPUBComics': 0, 'webBookControl': 0, 'selfProduceIncentive': False}, 'reviewCount': 0, 'reviewLikeCount': 0, 'reviewCommentCount': 0, 'noteCount': 33, 'bookmarkCount': 0, 'sort': 1731690777}, {'bookId': 'MP_WXS_3938515368', 'book': {'bookId': 'MP_WXS_3938515368', 'title': '定焦One', 'author': '公众号', 'cover': 'http://wx.qlogo.cn/mmhead/Q3auHgzwzM4SSvlj4Zb9L2L6SQNTlexqf1MvDmrCcBXnXkBqoS9M5w/0', 'version': 1731629877, 'format': 'epub', 'type': 3, 'price': 0, 'originalPrice': 0, 'soldout': 0, 'bookStatus': 2, 'payType': 32, 'centPrice': 0, 'finished': 0, 'free': 1, 'mcardDiscount': 0, 'ispub': 0, 'cpid': 0, 'publishTime': '', 'hasLecture': 0, 'lastChapterIdx': 0, 'paperBook': {'skuId': ''}, 'copyrightChapterUids': [], 'blockSaveImg': 0, 'language': 'zh', 'hideUpdateTime': False, 'isEPUBComics': 0, 'webBookControl': 0, 'selfProduceIncentive': False}, 'reviewCount': 0, 'reviewLikeCount': 0, 'reviewCommentCount': 0, 'noteCount': 15, 'bookmarkCount': 0, 'sort': 1731687162}, {'bookId': '3300021860', 'book': {'bookId': '3300021860', 'title': '雷军传', 'author': '陈润', 'cover': 'https://cdn.weread.qq.com/weread/cover/60/3300021860/s_3300021860.jpg', 'version': 652015160, 'format': 'epub', 'type': 0, 'price': 24.5, 'originalPrice': 0, 'soldout': 0, 'bookStatus': 1, 'payType': 1048577, 'centPrice': 2450, 'finished': 1, 'free': 0, 'mcardDiscount': 0, 'ispub': 1, 'extra_type': 5, 'cpid': 14614486, 'publishTime': '2019-12-01 00:00:00', 'categories': [{'categoryId': 1100000, 'subCategoryId': 1100004, 'categoryType': 0, 'title': '经济理财-商业'}, {'categoryId': 500000, 'subCategoryId': 500001, 'categoryType': 0, 'title': '人物传记-财经人物'}], 'hasLecture': 0, 'lastChapterIdx': 84, 'paperBook': {'skuId': ''}, 'copyrightChapterUids': [2], 'blockSaveImg': 0, 'language': 'zh', 'hideUpdateTime': False, 'isEPUBComics': 0, 'webBookControl': 0, 'selfProduceIncentive': False}, 'reviewCount': 0, 'reviewLikeCount': 0, 'reviewCommentCount': 0, 'noteCount': 2, 'bookmarkCount': 0, 'sort': 1731517402}, {'bookId': 'MP_WXS_3582870021', 'book': {'bookId': 'MP_WXS_3582870021', 'title': '少数派', 'author': '公众号', 'cover': 'http://wx.qlogo.cn/mmhead/Q3auHgzwzM6bW6DyvNhnRiaU4Ftjp3GNGXVEvS7S9MN4QY2ZT0FTmeQ/0', 'version': 1731641716, 'format': 'epub', 'type': 3, 'price': 0, 'originalPrice': 0, 'soldout': 0, 'bookStatus': 2, 'payType': 32, 'centPrice': 0, 'finished': 0, 'free': 1, 'mcardDiscount': 0, 'ispub': 0, 'cpid': 0, 'publishTime': '', 'hasLecture': 0, 'lastChapterIdx': 0, 'paperBook': {'skuId': ''}, 'copyrightChapterUids': [], 'blockSaveImg': 0, 'language': 'zh', 'hideUpdateTime': False, 'isEPUBComics': 0, 'webBookControl': 0, 'selfProduceIncentive': False}, 'reviewCount': 0, 'reviewLikeCount': 0, 'reviewCommentCount': 0, 'noteCount': 5, 'bookmarkCount': 0, 'sort': 1731474644}, {'bookId': 'MP_WXS_3586776457', 'book': {'bookId': 'MP_WXS_3586776457', 'title': '程序员黎明', 'author': '公众号', 'cover': 'http://wx.qlogo.cn/mmhead/1gvL9ficRs1Fl5JGXypiaV5YRcibOPzeN0OX5wp3x1RvGnovibhU8N4VYkEXVNBT508tpQ2V3tf97o4/0', 'version': 1731815328, 'format': 'epub', 'type': 3, 'price': 0, 'originalPrice': 0, 'soldout': 0, 'bookStatus': 2, 'payType': 32, 'centPrice': 0, 'finished': 0, 'free': 1, 'mcardDiscount': 0, 'ispub': 0, 'cpid': 0, 'publishTime': '', 'hasLecture': 0, 'lastChapterIdx': 0, 'paperBook': {'skuId': ''}, 'copyrightChapterUids': [], 'blockSaveImg': 0, 'language': 'zh', 'hideUpdateTime': False, 'isEPUBComics': 0, 'webBookControl': 0, 'selfProduceIncentive': False}, 'reviewCount': 0, 'reviewLikeCount': 0, 'reviewCommentCount': 0, 'noteCount': 1, 'bookmarkCount': 0, 'sort': 1731474201}, {'bookId': 'MP_WXS_3584400999', 'book': {'bookId': 'MP_WXS_3584400999', 'title': '凤凰网', 'author': '公众号', 'cover': 'http://wx.qlogo.cn/mmhead/Q3auHgzwzM6HV00zJW9yjkqv3Rc2ce4ogrGzP9tb0mMYDOUK9aOfcA/0', 'version': 1731837567, 'format': 'epub', 'type': 3, 'price': 0, 'originalPrice': 0, 'soldout': 0, 'bookStatus': 2, 'payType': 32, 'centPrice': 0, 'finished': 0, 'free': 1, 'mcardDiscount': 0, 'ispub': 0, 'cpid': 0, 'publishTime': '', 'hasLecture': 0, 'lastChapterIdx': 0, 'paperBook': {'skuId': ''}, 'copyrightChapterUids': [], 'blockSaveImg': 0, 'language': 'zh', 'hideUpdateTime': False, 'isEPUBComics': 0, 'webBookControl': 0, 'selfProduceIncentive': False}, 'reviewCount': 0, 'reviewLikeCount': 0, 'reviewCommentCount': 0, 'noteCount': 20, 'bookmarkCount': 0, 'sort': 1731473835}, {'bookId': 'MP_WXS_3224065282', 'book': {'bookId': 'MP_WXS_3224065282', 'title': '知识分子', 'author': '公众号', 'cover': 'http://wx.qlogo.cn/mmhead/Q3auHgzwzM4lnbnbLlRUxicmyXia8Su6qtGs9IPYwrV7icXiaUTiblmGycw/0', 'version': 1731771742, 'format': 'epub', 'type': 3, 'price': 0, 'originalPrice': 0, 'soldout': 0, 'bookStatus': 2, 'payType': 32, 'centPrice': 0, 'finished': 0, 'free': 1, 'mcardDiscount': 0, 'ispub': 0, 'cpid': 0, 'publishTime': '', 'hasLecture': 0, 'lastChapterIdx': 0, 'paperBook': {'skuId': ''}, 'copyrightChapterUids': [], 'blockSaveImg': 0, 'language': 'zh', 'hideUpdateTime': False, 'isEPUBComics': 0, 'webBookControl': 0, 'selfProduceIncentive': False}, 'reviewCount': 0, 'reviewLikeCount': 0, 'reviewCommentCount': 0, 'noteCount': 2, 'bookmarkCount': 0, 'sort': 1731472401}, {'bookId': 'MP_WXS_3934589433', 'book': {'bookId': 'MP_WXS_3934589433', 'title': '骑行圈', 'author': '公众号', 'cover': 'http://wx.qlogo.cn/mmhead/Q3auHgzwzM7eavtv0NenxcyXPIgnV69TbUuqmFfJ0wPTjgFclVZnWQ/0', 'version': 1731757907, 'format': 'epub', 'type': 3, 'price': 0, 'originalPrice': 0, 'soldout': 0, 'bookStatus': 2, 'payType': 32, 'centPrice': 0, 'finished': 0, 'free': 1, 'mcardDiscount': 0, 'ispub': 0, 'cpid': 0, 'publishTime': '', 'hasLecture': 0, 'lastChapterIdx': 0, 'paperBook': {'skuId': ''}, 'copyrightChapterUids': [], 'blockSaveImg': 0, 'language': 'zh', 'hideUpdateTime': False, 'isEPUBComics': 0, 'webBookControl': 0, 'selfProduceIncentive': False}, 'reviewCount': 0, 'reviewLikeCount': 0, 'reviewCommentCount': 0, 'noteCount': 8, 'bookmarkCount': 0, 'sort': 1731472028}, {'bookId': 'MP_WXS_3249188119', 'book': {'bookId': 'MP_WXS_3249188119', 'title': '火锅聊车', 'author': '公众号', 'cover': 'http://wx.qlogo.cn/mmhead/Q3auHgzwzM6fqE7yCK5k2VnWTjhoRiaean427mMHeociaSkDye8v8qBg/0', 'version': 1731639755, 'format': 'epub', 'type': 3, 'price': 0, 'originalPrice': 0, 'soldout': 0, 'bookStatus': 2, 'payType': 32, 'centPrice': 0, 'finished': 0, 'free': 1, 'mcardDiscount': 0, 'ispub': 0, 'cpid': 0, 'publishTime': '', 'hasLecture': 0, 'lastChapterIdx': 0, 'paperBook': {'skuId': ''}, 'copyrightChapterUids': [], 'blockSaveImg': 0, 'language': 'zh', 'hideUpdateTime': False, 'isEPUBComics': 0, 'webBookControl': 0, 'selfProduceIncentive': False}, 'reviewCount': 0, 'reviewLikeCount': 0, 'reviewCommentCount': 0, 'noteCount': 1, 'bookmarkCount': 0, 'sort': 1731471708}, {'bookId': 'MP_WXS_2398330323', 'book': {'bookId': 'MP_WXS_2398330323', 'title': '新周刊', 'author': '公众号', 'cover': 'http://wx.qlogo.cn/mmhead/Q3auHgzwzM42TvbuqRNPquFIhM5S2Q5LJpzCWUuEfT5nQoZHc8vbsw/0', 'version': 1731839572, 'format': 'epub', 'type': 3, 'price': 0, 'originalPrice': 0, 'soldout': 0, 'bookStatus': 2, 'payType': 32, 'centPrice': 0, 'finished': 0, 'free': 1, 'mcardDiscount': 0, 'ispub': 0, 'cpid': 0, 'publishTime': '', 'hasLecture': 0, 'lastChapterIdx': 0, 'paperBook': {'skuId': ''}, 'copyrightChapterUids': [], 'blockSaveImg': 0, 'language': 'zh', 'hideUpdateTime': False, 'isEPUBComics': 0, 'webBookControl': 0, 'selfProduceIncentive': False}, 'reviewCount': 0, 'reviewLikeCount': 0, 'reviewCommentCount': 0, 'noteCount': 38, 'bookmarkCount': 0, 'sort': 1731471535}, {'bookId': 'MP_WXS_2390553873', 'book': {'bookId': 'MP_WXS_2390553873', 'title': '中国新闻周刊', 'author': '公众号', 'cover': 'http://wx.qlogo.cn/mmhead/Q3auHgzwzM7IPhF5bMgNmQicGMYMOWiciaZp8Npj7VspibYbuGyNa4G0Tw/0', 'version': 1731828081, 'format': 'epub', 'type': 3, 'price': 0, 'originalPrice': 0, 'soldout': 0, 'bookStatus': 2, 'payType': 32, 'centPrice': 0, 'finished': 0, 'free': 1, 'mcardDiscount': 0, 'ispub': 0, 'cpid': 0, 'publishTime': '', 'hasLecture': 0, 'lastChapterIdx': 0, 'paperBook': {'skuId': ''}, 'copyrightChapterUids': [], 'blockSaveImg': 0, 'language': 'zh', 'hideUpdateTime': False, 'isEPUBComics': 0, 'webBookControl': 0, 'selfProduceIncentive': False}, 'reviewCount': 0, 'reviewLikeCount': 0, 'reviewCommentCount': 0, 'noteCount': 25, 'bookmarkCount': 0, 'sort': 1731460057}, {'bookId': 'CB_4TB5Kr5NsFSN6rj6sw5miDSE', 'book': {'bookId': 'CB_4TB5Kr5NsFSN6rj6sw5miDSE', 'title': '耕伟的雅思阅读加速营', 'author': '', 'cover': 'https://weread-1258476243.file.myqcloud.com/app/assets/bookcover/book_cover_default_imported_06.png', 'version': 429353056, 'format': 'epub', 'type': 0, 'price': 0, 'originalPrice': 0, 'soldout': 0, 'bookStatus': 1, 'payType': 33, 'centPrice': 0, 'finished': 1, 'free': 1, 'mcardDiscount': 0, 'ispub': 0, 'cpid': 0, 'publishTime': '', 'hasLecture': 0, 'lastChapterIdx': 7, 'paperBook': {'skuId': ''}, 'copyrightChapterUids': [], 'limitShareChat': 0, 'blockSaveImg': 0, 'language': 'zh-wr', 'hideUpdateTime': False, 'isEPUBComics': 0, 'webBookControl': 0, 'selfProduceIncentive': False}, 'reviewCount': 3, 'reviewLikeCount': 0, 'reviewCommentCount': 0, 'noteCount': 562, 'bookmarkCount': 0, 'sort': 1731456293}, {'bookId': 'MP_WXS_3264997043', 'book': {'bookId': 'MP_WXS_3264997043', 'title': '36氪', 'author': '公众号', 'cover': 'http://wx.qlogo.cn/mmhead/Q3auHgzwzM6bia44ArPNMqFIeUFznyuic1uaRBHxkkppnTnnYpkPVSXA/0', 'version': 1731833236, 'format': 'epub', 'type': 3, 'price': 0, 'originalPrice': 0, 'soldout': 0, 'bookStatus': 2, 'payType': 32, 'centPrice': 0, 'finished': 0, 'free': 1, 'mcardDiscount': 0, 'ispub': 0, 'cpid': 0, 'publishTime': '', 'hasLecture': 0, 'lastChapterIdx': 0, 'paperBook': {'skuId': ''}, 'copyrightChapterUids': [], 'blockSaveImg': 0, 'language': 'zh', 'hideUpdateTime': False, 'isEPUBComics': 0, 'webBookControl': 0, 'selfProduceIncentive': False}, 'reviewCount': 0, 'reviewLikeCount': 0, 'reviewCommentCount': 0, 'noteCount': 6, 'bookmarkCount': 0, 'sort': 1731433994}, {'bookId': 'MP_WXS_3080306716', 'book': {'bookId': 'MP_WXS_3080306716', 'title': '显微故事', 'author': '公众号', 'cover': 'http://wx.qlogo.cn/mmhead/Q3auHgzwzM6SBYWaE9MWG5XM5HcUfehEkMVBN58ExRvlyGaLY7KFKg/0', 'version': 1731593448, 'format': 'epub', 'type': 3, 'price': 0, 'originalPrice': 0, 'soldout': 0, 'bookStatus': 2, 'payType': 32, 'centPrice': 0, 'finished': 0, 'free': 1, 'mcardDiscount': 0, 'ispub': 0, 'cpid': 0, 'publishTime': '', 'hasLecture': 0, 'lastChapterIdx': 0, 'paperBook': {'skuId': ''}, 'copyrightChapterUids': [], 'blockSaveImg': 0, 'language': 'zh', 'hideUpdateTime': False, 'isEPUBComics': 0, 'webBookControl': 0, 'selfProduceIncentive': False}, 'reviewCount': 0, 'reviewLikeCount': 0, 'reviewCommentCount': 0, 'noteCount': 2, 'bookmarkCount': 0, 'sort': 1731389047}, {'bookId': 'MP_WXS_2394595381', 'book': {'bookId': 'MP_WXS_2394595381', 'title': '财经杂志', 'author': '公众号', 'cover': 'http://wx.qlogo.cn/mmhead/Q3auHgzwzM6gaRdUcnARJGibV4V56kclIibgdhPd9bNMVzEhTO0KgKTg/0', 'version': 1731836836, 'format': 'epub', 'type': 3, 'price': 0, 'originalPrice': 0, 'soldout': 0, 'bookStatus': 2, 'payType': 32, 'centPrice': 0, 'finished': 0, 'free': 1, 'mcardDiscount': 0, 'ispub': 0, 'cpid': 0, 'publishTime': '', 'hasLecture': 0, 'lastChapterIdx': 0, 'paperBook': {'skuId': ''}, 'copyrightChapterUids': [], 'blockSaveImg': 0, 'language': 'zh', 'hideUpdateTime': False, 'isEPUBComics': 0, 'webBookControl': 0, 'selfProduceIncentive': False}, 'reviewCount': 0, 'reviewLikeCount': 0, 'reviewCommentCount': 0, 'noteCount': 22, 'bookmarkCount': 0, 'sort': 1731170985}, {'bookId': 'MP_WXS_3093258134', 'book': {'bookId': 'MP_WXS_3093258134', 'title': '财经', 'author': '公众号', 'cover': 'http://wx.qlogo.cn/mmhead/Q3auHgzwzM5UjefmLcxIfdDZfgFM5chGUlibia6p2WZfzm1ZfXZwc0HA/0', 'version': 1731820630, 'format': 'epub', 'type': 3, 'price': 0, 'originalPrice': 0, 'soldout': 0, 'bookStatus': 2, 'payType': 32, 'centPrice': 0, 'finished': 0, 'free': 1, 'mcardDiscount': 0, 'ispub': 0, 'cpid': 0, 'publishTime': '', 'hasLecture': 0, 'lastChapterIdx': 0, 'paperBook': {'skuId': ''}, 'copyrightChapterUids': [], 'blockSaveImg': 0, 'language': 'zh', 'hideUpdateTime': False, 'isEPUBComics': 0, 'webBookControl': 0, 'selfProduceIncentive': False}, 'reviewCount': 0, 'reviewLikeCount': 0, 'reviewCommentCount': 0, 'noteCount': 15, 'bookmarkCount': 0, 'sort': 1731168994}, {'bookId': 'MP_WXS_2394601857', 'book': {'bookId': 'MP_WXS_2394601857', 'title': '嗅态', 'author': '公众号', 'cover': 'http://wx.qlogo.cn/mmhead/UDa9R1yl9UbcWMEBd5eu3me7P3qIhe6QVbWQs4ExYOo4jLz8sicziazC6eHs6D9HBFYsIMHKQpb6w/0', 'version': 1731421004, 'format': 'epub', 'type': 3, 'price': 0, 'originalPrice': 0, 'soldout': 0, 'bookStatus': 2, 'payType': 32, 'centPrice': 0, 'finished': 0, 'free': 1, 'mcardDiscount': 0, 'ispub': 0, 'cpid': 0, 'publishTime': '', 'hasLecture': 0, 'lastChapterIdx': 0, 'paperBook': {'skuId': ''}, 'copyrightChapterUids': [], 'blockSaveImg': 0, 'language': 'zh', 'hideUpdateTime': False, 'isEPUBComics': 0, 'webBookControl': 0, 'selfProduceIncentive': False}, 'reviewCount': 0, 'reviewLikeCount': 0, 'reviewCommentCount': 0, 'noteCount': 2, 'bookmarkCount': 0, 'sort': 1731139016}, {'bookId': 'MP_WXS_699115', 'book': {'bookId': 'MP_WXS_699115', 'title': '南方周末', 'author': '公众号', 'cover': 'http://wx.qlogo.cn/mmhead/Jszx49YbsxRfeb75zAHCrMiaFlEBUtXRGTNQX9z9YibrE/0', 'version': 1731831457, 'format': 'epub', 'type': 3, 'price': 0, 'originalPrice': 0, 'soldout': 0, 'bookStatus': 2, 'payType': 32, 'centPrice': 0, 'finished': 0, 'free': 1, 'mcardDiscount': 0, 'ispub': 0, 'cpid': 0, 'publishTime': '', 'hasLecture': 0, 'lastChapterIdx': 0, 'paperBook': {'skuId': ''}, 'copyrightChapterUids': [], 'blockSaveImg': 0, 'language': 'zh', 'hideUpdateTime': False, 'isEPUBComics': 0, 'webBookControl': 0, 'selfProduceIncentive': False}, 'reviewCount': 0, 'reviewLikeCount': 0, 'reviewCommentCount': 0, 'noteCount': 76, 'bookmarkCount': 0, 'sort': 1731041464}, {'bookId': 'MP_WXS_2394297967', 'book': {'bookId': 'MP_WXS_2394297967', 'title': '三联电子厂Pro', 'author': '公众号', 'cover': 'http://wx.qlogo.cn/mmhead/AhLk989Zrl1r71Mca6YtQn2UUGDJLHD2OhhW6zYLo4dQgaVDALM2XibqEjyWDdtdPCGbicoY0ibLPE/0', 'version': 1731579025, 'format': 'epub', 'type': 3, 'price': 0, 'originalPrice': 0, 'soldout': 0, 'bookStatus': 2, 'payType': 32, 'centPrice': 0, 'finished': 0, 'free': 1, 'mcardDiscount': 0, 'ispub': 0, 'cpid': 0, 'publishTime': '', 'hasLecture': 0, 'lastChapterIdx': 0, 'paperBook': {'skuId': ''}, 'copyrightChapterUids': [], 'blockSaveImg': 0, 'language': 'zh', 'hideUpdateTime': False, 'isEPUBComics': 0, 'webBookControl': 0, 'selfProduceIncentive': False}, 'reviewCount': 0, 'reviewLikeCount': 0, 'reviewCommentCount': 0, 'noteCount': 19, 'bookmarkCount': 0, 'sort': 1731034980}, {'bookId': 'MP_WXS_3894866322', 'book': {'bookId': 'MP_WXS_3894866322', 'title': 'DT商业观察', 'author': '公众号', 'cover': 'http://wx.qlogo.cn/mmhead/Q3auHgzwzM6z468YTILs7oPL3EhkSnO256YPwxFY8SeJiaYp5skULpA/0', 'version': 1731678504, 'format': 'epub', 'type': 3, 'price': 0, 'originalPrice': 0, 'soldout': 0, 'bookStatus': 2, 'payType': 32, 'centPrice': 0, 'finished': 0, 'free': 1, 'mcardDiscount': 0, 'ispub': 0, 'cpid': 0, 'publishTime': '', 'hasLecture': 0, 'lastChapterIdx': 0, 'paperBook': {'skuId': ''}, 'copyrightChapterUids': [], 'blockSaveImg': 0, 'language': 'zh', 'hideUpdateTime': False, 'isEPUBComics': 0, 'webBookControl': 0, 'selfProduceIncentive': False}, 'reviewCount': 0, 'reviewLikeCount': 0, 'reviewCommentCount': 0, 'noteCount': 19, 'bookmarkCount': 0, 'sort': 1730991891}, {'bookId': 'MP_WXS_3867740377', 'book': {'bookId': 'MP_WXS_3867740377', 'title': '南风窗', 'author': '公众号', 'cover': 'http://wx.qlogo.cn/mmhead/Q3auHgzwzM6HSg75RrjBhK55zZt84RicE2b62m56XqwZVQnHFCgbvOg/0', 'version': 1731817873, 'format': 'epub', 'type': 3, 'price': 0, 'originalPrice': 0, 'soldout': 0, 'bookStatus': 2, 'payType': 32, 'centPrice': 0, 'finished': 0, 'free': 1, 'mcardDiscount': 0, 'ispub': 0, 'cpid': 0, 'publishTime': '', 'hasLecture': 0, 'lastChapterIdx': 0, 'paperBook': {'skuId': ''}, 'copyrightChapterUids': [], 'blockSaveImg': 0, 'language': 'zh', 'hideUpdateTime': False, 'isEPUBComics': 0, 'webBookControl': 0, 'selfProduceIncentive': False}, 'reviewCount': 0, 'reviewLikeCount': 0, 'reviewCommentCount': 0, 'noteCount': 56, 'bookmarkCount': 0, 'sort': 1730991110}, {'bookId': 'MP_WXS_3299372324', 'book': {'bookId': 'MP_WXS_3299372324', 'title': '飞总聊IT', 'author': '公众号', 'cover': 'http://wx.qlogo.cn/mmhead/Q3auHgzwzM5IFAicU2DwrfvCGCvlsrlqosjAo8vksA3kdH7nnL1JPWQ/0', 'version': 1731803120, 'format': 'epub', 'type': 3, 'price': 0, 'originalPrice': 0, 'soldout': 0, 'bookStatus': 2, 'payType': 32, 'centPrice': 0, 'finished': 0, 'free': 1, 'mcardDiscount': 0, 'ispub': 0, 'cpid': 0, 'publishTime': '', 'hasLecture': 0, 'lastChapterIdx': 0, 'paperBook': {'skuId': ''}, 'copyrightChapterUids': [], 'blockSaveImg': 0, 'language': 'zh', 'hideUpdateTime': False, 'isEPUBComics': 0, 'webBookControl': 0, 'selfProduceIncentive': False}, 'reviewCount': 0, 'reviewLikeCount': 0, 'reviewCommentCount': 0, 'noteCount': 1, 'bookmarkCount': 0, 'sort': 1730953137}, {'bookId': 'MP_WXS_3201771057', 'book': {'bookId': 'MP_WXS_3201771057', 'title': '功率骑行那些事', 'author': '公众号', 'cover': 'http://wx.qlogo.cn/mmhead/Q3auHgzwzM7cdBniaz4f5RTXVej1gGVT6sr2u6EtCgz9B5L49jQadSA/0', 'version': 1731728442, 'format': 'epub', 'type': 3, 'price': 0, 'originalPrice': 0, 'soldout': 0, 'bookStatus': 2, 'payType': 32, 'centPrice': 0, 'finished': 0, 'free': 1, 'mcardDiscount': 0, 'ispub': 0, 'cpid': 0, 'publishTime': '', 'hasLecture': 0, 'lastChapterIdx': 0, 'paperBook': {'skuId': ''}, 'copyrightChapterUids': [], 'blockSaveImg': 0, 'language': 'zh', 'hideUpdateTime': False, 'isEPUBComics': 0, 'webBookControl': 0, 'selfProduceIncentive': False}, 'reviewCount': 0, 'reviewLikeCount': 0, 'reviewCommentCount': 0, 'noteCount': 3, 'bookmarkCount': 0, 'sort': 1730823078}, {'bookId': 'MP_WXS_2397274880', 'book': {'bookId': 'MP_WXS_2397274880', 'title': '人民网', 'author': '公众号', 'cover': 'http://wx.qlogo.cn/mmhead/Q3auHgzwzM7fyU4GApMpvWanVpMHA15fwyziaEqORgdqOZWGR2UKIuw/0', 'version': 1731844353, 'format': 'epub', 'type': 3, 'price': 0, 'originalPrice': 0, 'soldout': 0, 'bookStatus': 2, 'payType': 32, 'centPrice': 0, 'finished': 0, 'free': 1, 'mcardDiscount': 0, 'ispub': 0, 'cpid': 0, 'publishTime': '', 'hasLecture': 0, 'lastChapterIdx': 0, 'paperBook': {'skuId': ''}, 'copyrightChapterUids': [], 'blockSaveImg': 0, 'language': 'zh', 'hideUpdateTime': False, 'isEPUBComics': 0, 'webBookControl': 0, 'selfProduceIncentive': False}, 'reviewCount': 0, 'reviewLikeCount': 0, 'reviewCommentCount': 0, 'noteCount': 1, 'bookmarkCount': 0, 'sort': 1730822383}, {'bookId': 'MP_WXS_3076847139', 'book': {'bookId': 'MP_WXS_3076847139', 'title': '有意思报告', 'author': '公众号', 'cover': 'http://wx.qlogo.cn/mmhead/Q3auHgzwzM5lP4pVb0vSVibtSptr8FNWsXZIG0GpxGv7gLY18BnW5Qw/0', 'version': 1731839481, 'format': 'epub', 'type': 3, 'price': 0, 'originalPrice': 0, 'soldout': 0, 'bookStatus': 2, 'payType': 32, 'centPrice': 0, 'finished': 0, 'free': 1, 'mcardDiscount': 0, 'ispub': 0, 'cpid': 0, 'publishTime': '', 'hasLecture': 0, 'lastChapterIdx': 0, 'paperBook': {'skuId': ''}, 'copyrightChapterUids': [], 'blockSaveImg': 0, 'language': 'zh', 'hideUpdateTime': False, 'isEPUBComics': 0, 'webBookControl': 0, 'selfProduceIncentive': False}, 'reviewCount': 0, 'reviewLikeCount': 0, 'reviewCommentCount': 0, 'noteCount': 16, 'bookmarkCount': 0, 'sort': 1730783042}, {'bookId': 'MP_WXS_3249642754', 'book': {'bookId': 'MP_WXS_3249642754', 'title': '小方说跑步', 'author': '公众号', 'cover': 'http://wx.qlogo.cn/mmhead/Q3auHgzwzM7mRSqEGMT4TdrNibwbxAaJVQyAziaOWXibpqupm7ARqa87Q/0', 'version': 1731732472, 'format': 'epub', 'type': 3, 'price': 0, 'originalPrice': 0, 'soldout': 0, 'bookStatus': 2, 'payType': 32, 'centPrice': 0, 'finished': 0, 'free': 1, 'mcardDiscount': 0, 'ispub': 0, 'cpid': 0, 'publishTime': '', 'hasLecture': 0, 'lastChapterIdx': 0, 'paperBook': {'skuId': ''}, 'copyrightChapterUids': [], 'blockSaveImg': 0, 'language': 'zh', 'hideUpdateTime': False, 'isEPUBComics': 0, 'webBookControl': 0, 'selfProduceIncentive': False}, 'reviewCount': 0, 'reviewLikeCount': 0, 'reviewCommentCount': 0, 'noteCount': 1, 'bookmarkCount': 0, 'sort': 1730782286}, {'bookId': 'MP_WXS_2398714628', 'book': {'bookId': 'MP_WXS_2398714628', 'title': '文森地产嗅', 'author': '公众号', 'cover': 'http://wx.qlogo.cn/mmhead/Q3auHgzwzM5BqpwibCsPrB3mjgzr1t7nVRPRvyqMG25ic8BGaRZ28D6g/0', 'version': 1730507211, 'format': 'epub', 'type': 3, 'price': 0, 'originalPrice': 0, 'soldout': 0, 'bookStatus': 2, 'payType': 32, 'centPrice': 0, 'finished': 0, 'free': 1, 'mcardDiscount': 0, 'ispub': 0, 'cpid': 0, 'publishTime': '', 'hasLecture': 0, 'lastChapterIdx': 0, 'paperBook': {'skuId': ''}, 'copyrightChapterUids': [], 'blockSaveImg': 0, 'language': 'zh', 'hideUpdateTime': False, 'isEPUBComics': 0, 'webBookControl': 0, 'selfProduceIncentive': False}, 'reviewCount': 0, 'reviewLikeCount': 0, 'reviewCommentCount': 0, 'noteCount': 4, 'bookmarkCount': 0, 'sort': 1730781914}, {'bookId': 'MP_WXS_2397003540', 'book': {'bookId': 'MP_WXS_2397003540', 'title': '华尔街见闻', 'author': '公众号', 'cover': 'http://wx.qlogo.cn/mmhead/Q3auHgzwzM6rXJG1cGpkjAWuiadcdlsJue9nAateRWQC7RJhECDRjicQ/0', 'version': 1731752194, 'format': 'epub', 'type': 3, 'price': 0, 'originalPrice': 0, 'soldout': 0, 'bookStatus': 2, 'payType': 32, 'centPrice': 0, 'finished': 0, 'free': 1, 'mcardDiscount': 0, 'ispub': 0, 'cpid': 0, 'publishTime': '', 'hasLecture': 0, 'lastChapterIdx': 0, 'paperBook': {'skuId': ''}, 'copyrightChapterUids': [], 'blockSaveImg': 0, 'language': 'zh', 'hideUpdateTime': False, 'isEPUBComics': 0, 'webBookControl': 0, 'selfProduceIncentive': False}, 'reviewCount': 0, 'reviewLikeCount': 0, 'reviewCommentCount': 0, 'noteCount': 12, 'bookmarkCount': 0, 'sort': 1730774464}, {'bookId': 'CB_39J5Ph5S1FSN6rj6sw8br1uz', 'book': {'bookId': 'CB_39J5Ph5S1FSN6rj6sw8br1uz', 'title': '耕伟16天写作训练营', 'author': '', 'cover': 'https://weread-1258476243.file.myqcloud.com/app/assets/bookcover/book_cover_default_imported_05.png', 'version': 54220144, 'format': 'epub', 'type': 0, 'price': 0, 'originalPrice': 0, 'soldout': 0, 'bookStatus': 1, 'payType': 33, 'centPrice': 0, 'finished': 1, 'free': 1, 'mcardDiscount': 0, 'ispub': 0, 'cpid': 0, 'publishTime': '', 'hasLecture': 0, 'lastChapterIdx': 2, 'paperBook': {'skuId': ''}, 'copyrightChapterUids': [], 'hasKeyPoint': True, 'limitShareChat': 0, 'blockSaveImg': 0, 'language': 'zh-wr', 'hideUpdateTime': False, 'isEPUBComics': 0, 'webBookControl': 0, 'selfProduceIncentive': False}, 'reviewCount': 0, 'reviewLikeCount': 0, 'reviewCommentCount': 0, 'noteCount': 12, 'bookmarkCount': 0, 'sort': 1730727471}, {'bookId': 'MP_WXS_3582869260', 'book': {'bookId': 'MP_WXS_3582869260', 'title': '浪潮工作室', 'author': '公众号', 'cover': 'http://wx.qlogo.cn/mmhead/Q3auHgzwzM6icxbrtAWgpZbaXSR60kXLJAs0A7gnSIWLDRR04xaYlZQ/0', 'version': 1731728458, 'format': 'epub', 'type': 3, 'price': 0, 'originalPrice': 0, 'soldout': 0, 'bookStatus': 2, 'payType': 32, 'centPrice': 0, 'finished': 0, 'free': 1, 'mcardDiscount': 0, 'ispub': 0, 'cpid': 0, 'publishTime': '', 'hasLecture': 0, 'lastChapterIdx': 0, 'paperBook': {'skuId': ''}, 'copyrightChapterUids': [], 'blockSaveImg': 0, 'language': 'zh', 'hideUpdateTime': False, 'isEPUBComics': 0, 'webBookControl': 0, 'selfProduceIncentive': False}, 'reviewCount': 0, 'reviewLikeCount': 0, 'reviewCommentCount': 0, 'noteCount': 21, 'bookmarkCount': 0, 'sort': 1730716530}, {'bookId': 'MP_WXS_3004051383', 'book': {'bookId': 'MP_WXS_3004051383', 'title': 'CEO来信', 'author': '公众号', 'cover': 'http://wx.qlogo.cn/mmhead/Q3auHgzwzM6sPgE9IJpRANymlyMmugzDRYwef1nUnZa6017sWKRDPQ/0', 'version': 1731775833, 'format': 'epub', 'type': 3, 'price': 0, 'originalPrice': 0, 'soldout': 0, 'bookStatus': 2, 'payType': 32, 'centPrice': 0, 'finished': 0, 'free': 1, 'mcardDiscount': 0, 'ispub': 0, 'cpid': 0, 'publishTime': '', 'hasLecture': 0, 'lastChapterIdx': 0, 'paperBook': {'skuId': ''}, 'copyrightChapterUids': [], 'blockSaveImg': 0, 'language': 'zh', 'hideUpdateTime': False, 'isEPUBComics': 0, 'webBookControl': 0, 'selfProduceIncentive': False}, 'reviewCount': 0, 'reviewLikeCount': 0, 'reviewCommentCount': 0, 'noteCount': 24, 'bookmarkCount': 0, 'sort': 1730598040}, {'bookId': 'MP_WXS_3227786781', 'book': {'bookId': 'MP_WXS_3227786781', 'title': '盐财经', 'author': '公众号', 'cover': 'http://wx.qlogo.cn/mmhead/Q3auHgzwzM4diaoFWvyCnZlE5RR7icOAjCBOUKjZticn8gTobIc8micRlg/0', 'version': 1731663864, 'format': 'epub', 'type': 3, 'price': 0, 'originalPrice': 0, 'soldout': 0, 'bookStatus': 2, 'payType': 32, 'centPrice': 0, 'finished': 0, 'free': 1, 'mcardDiscount': 0, 'ispub': 0, 'cpid': 0, 'publishTime': '', 'hasLecture': 0, 'lastChapterIdx': 0, 'paperBook': {'skuId': ''}, 'copyrightChapterUids': [], 'blockSaveImg': 0, 'language': 'zh', 'hideUpdateTime': False, 'isEPUBComics': 0, 'webBookControl': 0, 'selfProduceIncentive': False}, 'reviewCount': 0, 'reviewLikeCount': 0, 'reviewCommentCount': 0, 'noteCount': 10, 'bookmarkCount': 0, 'sort': 1730595961}, {'bookId': 'MP_WXS_2399980242', 'book': {'bookId': 'MP_WXS_2399980242', 'title': '万叔港谈', 'author': '公众号', 'cover': 'http://wx.qlogo.cn/mmhead/Q3auHgzwzM5aaraXhqYFDLSmBUgSdKuiaAfMXO1PglqP8X93erE3oSA/0', 'version': 1731716154, 'format': 'epub', 'type': 3, 'price': 0, 'originalPrice': 0, 'soldout': 0, 'bookStatus': 2, 'payType': 32, 'centPrice': 0, 'finished': 0, 'free': 1, 'mcardDiscount': 0, 'ispub': 0, 'cpid': 0, 'publishTime': '', 'hasLecture': 0, 'lastChapterIdx': 0, 'paperBook': {'skuId': ''}, 'copyrightChapterUids': [], 'blockSaveImg': 0, 'language': 'zh', 'hideUpdateTime': False, 'isEPUBComics': 0, 'webBookControl': 0, 'selfProduceIncentive': False}, 'reviewCount': 0, 'reviewLikeCount': 0, 'reviewCommentCount': 0, 'noteCount': 1, 'bookmarkCount': 0, 'sort': 1730595393}, {'bookId': 'MP_WXS_2394542961', 'book': {'bookId': 'MP_WXS_2394542961', 'title': '连岳', 'author': '公众号', 'cover': 'http://wx.qlogo.cn/mmhead/Q3auHgzwzM4RswLiaZx6S1yMxkRGxTLv438pDQP809Bzu0hyvXAibooQ/0', 'version': 1731802041, 'format': 'epub', 'type': 3, 'price': 0, 'originalPrice': 0, 'soldout': 0, 'bookStatus': 2, 'payType': 32, 'centPrice': 0, 'finished': 0, 'free': 1, 'mcardDiscount': 0, 'ispub': 0, 'cpid': 0, 'publishTime': '', 'hasLecture': 0, 'lastChapterIdx': 0, 'paperBook': {'skuId': ''}, 'copyrightChapterUids': [], 'blockSaveImg': 0, 'language': 'zh', 'hideUpdateTime': False, 'isEPUBComics': 0, 'webBookControl': 0, 'selfProduceIncentive': False}, 'reviewCount': 0, 'reviewLikeCount': 0, 'reviewCommentCount': 0, 'noteCount': 1, 'bookmarkCount': 0, 'sort': 1730535488}, {'bookId': 'MP_WXS_2390323860', 'book': {'bookId': 'MP_WXS_2390323860', 'title': '十点读书', 'author': '公众号', 'cover': 'http://wx.qlogo.cn/mmhead/Q3auHgzwzM7BmxMfFQA3ic4p0H3Syd79W0p8Z6RnA9WnHcTTNrfPxSw/0', 'version': 1731836406, 'format': 'epub', 'type': 3, 'price': 0, 'originalPrice': 0, 'soldout': 0, 'bookStatus': 2, 'payType': 32, 'centPrice': 0, 'finished': 0, 'free': 1, 'mcardDiscount': 0, 'ispub': 0, 'cpid': 0, 'publishTime': '', 'authorVids': '18500042', 'hasLecture': 0, 'lastChapterIdx': 0, 'paperBook': {'skuId': ''}, 'copyrightChapterUids': [], 'blockSaveImg': 0, 'language': 'zh', 'hideUpdateTime': False, 'isEPUBComics': 0, 'webBookControl': 0, 'selfProduceIncentive': False}, 'reviewCount': 0, 'reviewLikeCount': 0, 'reviewCommentCount': 0, 'noteCount': 12, 'bookmarkCount': 0, 'sort': 1730534084}, {'bookId': 'MP_WXS_3074197826', 'book': {'bookId': 'MP_WXS_3074197826', 'title': 'ali老蒋说', 'author': '公众号', 'cover': 'http://wx.qlogo.cn/mmhead/SQd7RF5caa2uxPRKoIRl6sib8SZUjzFN4KDcOibzBvc2LHwuKLyYrF8xwp4RAiac8LxgDWpreBpYEE/0', 'version': 1731764387, 'format': 'epub', 'type': 3, 'price': 0, 'originalPrice': 0, 'soldout': 0, 'bookStatus': 2, 'payType': 32, 'centPrice': 0, 'finished': 0, 'free': 1, 'mcardDiscount': 0, 'ispub': 0, 'cpid': 0, 'publishTime': '', 'hasLecture': 0, 'lastChapterIdx': 0, 'paperBook': {'skuId': ''}, 'copyrightChapterUids': [], 'blockSaveImg': 0, 'language': 'zh', 'hideUpdateTime': False, 'isEPUBComics': 0, 'webBookControl': 0, 'selfProduceIncentive': False}, 'reviewCount': 0, 'reviewLikeCount': 0, 'reviewCommentCount': 0, 'noteCount': 13, 'bookmarkCount': 0, 'sort': 1730533305}, {'bookId': 'MP_WXS_3933680401', 'book': {'bookId': 'MP_WXS_3933680401', 'title': '失忆闰土', 'author': '公众号', 'cover': 'http://wx.qlogo.cn/mmhead/VzQsdzsGScMmZs9ZIjmtCxaxgcOxa4AUdfvMmTLtWUBU6GZVtYRPR0s9icBjYsNcuCONXRSWicsuE/0', 'version': 1731841017, 'format': 'epub', 'type': 3, 'price': 0, 'originalPrice': 0, 'soldout': 0, 'bookStatus': 2, 'payType': 32, 'centPrice': 0, 'finished': 0, 'free': 1, 'mcardDiscount': 0, 'ispub': 0, 'cpid': 0, 'publishTime': '', 'hasLecture': 0, 'lastChapterIdx': 0, 'paperBook': {'skuId': ''}, 'copyrightChapterUids': [], 'blockSaveImg': 0, 'language': 'zh', 'hideUpdateTime': False, 'isEPUBComics': 0, 'webBookControl': 0, 'selfProduceIncentive': False}, 'reviewCount': 0, 'reviewLikeCount': 0, 'reviewCommentCount': 0, 'noteCount': 5, 'bookmarkCount': 0, 'sort': 1730519080}, {'bookId': 'MP_WXS_3097390524', 'book': {'bookId': 'MP_WXS_3097390524', 'title': '北京门头沟', 'author': '公众号', 'cover': 'http://wx.qlogo.cn/mmhead/Q3auHgzwzM7I7hs3mOp2UnmJa6HtB022UFpVycEhljb28Rht0a5B7g/0', 'version': 1731807644, 'format': 'epub', 'type': 3, 'price': 0, 'originalPrice': 0, 'soldout': 0, 'bookStatus': 2, 'payType': 32, 'centPrice': 0, 'finished': 0, 'free': 1, 'mcardDiscount': 0, 'ispub': 0, 'cpid': 0, 'publishTime': '', 'hasLecture': 0, 'lastChapterIdx': 0, 'paperBook': {'skuId': ''}, 'copyrightChapterUids': [], 'blockSaveImg': 0, 'language': 'zh', 'hideUpdateTime': False, 'isEPUBComics': 0, 'webBookControl': 0, 'selfProduceIncentive': False}, 'reviewCount': 0, 'reviewLikeCount': 0, 'reviewCommentCount': 0, 'noteCount': 1, 'bookmarkCount': 0, 'sort': 1730468154}, {'bookId': 'MP_WXS_3234817419', 'book': {'bookId': 'MP_WXS_3234817419', 'title': '品牌观察官', 'author': '公众号', 'cover': 'http://wx.qlogo.cn/mmhead/Q3auHgzwzM4wkZibZOUicp34hPZI4D4iaJFy8VQd9nDsLar2bkic60xEyw/0', 'version': 1730885524, 'format': 'epub', 'type': 3, 'price': 0, 'originalPrice': 0, 'soldout': 0, 'bookStatus': 2, 'payType': 32, 'centPrice': 0, 'finished': 0, 'free': 1, 'mcardDiscount': 0, 'ispub': 0, 'cpid': 0, 'publishTime': '', 'hasLecture': 0, 'lastChapterIdx': 0, 'paperBook': {'skuId': ''}, 'copyrightChapterUids': [], 'blockSaveImg': 0, 'language': 'zh', 'hideUpdateTime': False, 'isEPUBComics': 0, 'webBookControl': 0, 'selfProduceIncentive': False}, 'reviewCount': 0, 'reviewLikeCount': 0, 'reviewCommentCount': 0, 'noteCount': 3, 'bookmarkCount': 0, 'sort': 1730439368}, {'bookId': 'MP_WXS_3210917349', 'book': {'bookId': 'MP_WXS_3210917349', 'title': 'Tspace特空间', 'author': '公众号', 'cover': 'http://wx.qlogo.cn/mmhead/Q3auHgzwzM6gwWZEIkXNEtJ01ibPDiasIZQCzemibnRXqSsxYAichmJHmg/0', 'version': 1731685355, 'format': 'epub', 'type': 3, 'price': 0, 'originalPrice': 0, 'soldout': 0, 'bookStatus': 2, 'payType': 32, 'centPrice': 0, 'finished': 0, 'free': 1, 'mcardDiscount': 0, 'ispub': 0, 'cpid': 0, 'publishTime': '', 'hasLecture': 0, 'lastChapterIdx': 0, 'paperBook': {'skuId': ''}, 'copyrightChapterUids': [], 'blockSaveImg': 0, 'language': 'zh', 'hideUpdateTime': False, 'isEPUBComics': 0, 'webBookControl': 0, 'selfProduceIncentive': False}, 'reviewCount': 0, 'reviewLikeCount': 0, 'reviewCommentCount': 0, 'noteCount': 9, 'bookmarkCount': 0, 'sort': 1730438890}, {'bookId': 'MP_WXS_3902208921', 'book': {'bookId': 'MP_WXS_3902208921', 'title': '电商报Pro', 'author': '公众号', 'cover': 'http://wx.qlogo.cn/mmhead/Q3auHgzwzM6F29xkZgCKS1iasZtBGdCGb1XPYrWPKBKICKslIgibt1Vw/0', 'version': 1731726865, 'format': 'epub', 'type': 3, 'price': 0, 'originalPrice': 0, 'soldout': 0, 'bookStatus': 2, 'payType': 32, 'centPrice': 0, 'finished': 0, 'free': 1, 'mcardDiscount': 0, 'ispub': 0, 'cpid': 0, 'publishTime': '', 'hasLecture': 0, 'lastChapterIdx': 0, 'paperBook': {'skuId': ''}, 'copyrightChapterUids': [], 'blockSaveImg': 0, 'language': 'zh', 'hideUpdateTime': False, 'isEPUBComics': 0, 'webBookControl': 0, 'selfProduceIncentive': False}, 'reviewCount': 0, 'reviewLikeCount': 0, 'reviewCommentCount': 0, 'noteCount': 9, 'bookmarkCount': 0, 'sort': 1730394844}, {'bookId': 'MP_WXS_3930438967', 'book': {'bookId': 'MP_WXS_3930438967', 'title': '数据多棱镜', 'author': '公众号', 'cover': 'http://wx.qlogo.cn/mmhead/thfLhcllFYoev110xYmD2ZILtkBMiaq6c7cPYnlIY6pxg7O6I8NakOCoNx3WUzpkKxwTGq1Sb2EM/0', 'version': 1731665566, 'format': 'epub', 'type': 3, 'price': 0, 'originalPrice': 0, 'soldout': 0, 'bookStatus': 2, 'payType': 32, 'centPrice': 0, 'finished': 0, 'free': 1, 'mcardDiscount': 0, 'ispub': 0, 'cpid': 0, 'publishTime': '', 'hasLecture': 0, 'lastChapterIdx': 0, 'paperBook': {'skuId': ''}, 'copyrightChapterUids': [], 'blockSaveImg': 0, 'language': 'zh', 'hideUpdateTime': False, 'isEPUBComics': 0, 'webBookControl': 0, 'selfProduceIncentive': False}, 'reviewCount': 0, 'reviewLikeCount': 0, 'reviewCommentCount': 0, 'noteCount': 19, 'bookmarkCount': 0, 'sort': 1730365383}, {'bookId': 'MP_WXS_3943739435', 'book': {'bookId': 'MP_WXS_3943739435', 'title': '文鼎鼎', 'author': '公众号', 'cover': 'http://wx.qlogo.cn/mmhead/WD4FduqfeKINgMib3EdSXHRkWmicYYE1k3wp2m6axTp2FAeWzvDAOXU3k87G4cBN92hHOxIogJyuI/0', 'version': 1731223624, 'format': 'epub', 'type': 3, 'price': 0, 'originalPrice': 0, 'soldout': 0, 'bookStatus': 2, 'payType': 32, 'centPrice': 0, 'finished': 0, 'free': 1, 'mcardDiscount': 0, 'ispub': 0, 'cpid': 0, 'publishTime': '', 'hasLecture': 0, 'lastChapterIdx': 0, 'paperBook': {'skuId': ''}, 'copyrightChapterUids': [], 'blockSaveImg': 0, 'language': 'zh', 'hideUpdateTime': False, 'isEPUBComics': 0, 'webBookControl': 0, 'selfProduceIncentive': False}, 'reviewCount': 0, 'reviewLikeCount': 0, 'reviewCommentCount': 0, 'noteCount': 10, 'bookmarkCount': 0, 'sort': 1730349308}, {'bookId': 'MP_WXS_3547513435', 'book': {'bookId': 'MP_WXS_3547513435', 'title': '十点人物志', 'author': '公众号', 'cover': 'http://wx.qlogo.cn/mmhead/Q3auHgzwzM6EyYwIYb8ue2QsjBIrFs8xtgIQ78152spYIo7cKeK0sQ/0', 'version': 1731743808, 'format': 'epub', 'type': 3, 'price': 0, 'originalPrice': 0, 'soldout': 0, 'bookStatus': 2, 'payType': 32, 'centPrice': 0, 'finished': 0, 'free': 1, 'mcardDiscount': 0, 'ispub': 0, 'cpid': 0, 'publishTime': '', 'hasLecture': 0, 'lastChapterIdx': 0, 'paperBook': {'skuId': ''}, 'copyrightChapterUids': [], 'blockSaveImg': 0, 'language': 'zh', 'hideUpdateTime': False, 'isEPUBComics': 0, 'webBookControl': 0, 'selfProduceIncentive': False}, 'reviewCount': 0, 'reviewLikeCount': 0, 'reviewCommentCount': 0, 'noteCount': 7, 'bookmarkCount': 0, 'sort': 1730303749}, {'bookId': 'CB_GDh5Uv5WAFSN6rj6sw3OoFY6', 'book': {'bookId': 'CB_GDh5Uv5WAFSN6rj6sw3OoFY6', 'title': '耕伟听力', 'author': '', 'cover': 'https://weread-1258476243.file.myqcloud.com/app/assets/bookcover/book_cover_default_imported_05.png', 'version': 2129925219, 'format': 'epub', 'type': 0, 'price': 0, 'originalPrice': 0, 'soldout': 0, 'bookStatus': 1, 'payType': 33, 'centPrice': 0, 'finished': 1, 'free': 1, 'mcardDiscount': 0, 'ispub': 0, 'cpid': 0, 'publishTime': '', 'hasLecture': 0, 'lastChapterIdx': 4, 'paperBook': {'skuId': ''}, 'copyrightChapterUids': [], 'limitShareChat': 0, 'blockSaveImg': 0, 'language': 'zh-wr', 'hideUpdateTime': False, 'isEPUBComics': 0, 'webBookControl': 0, 'selfProduceIncentive': False}, 'reviewCount': 43, 'reviewLikeCount': 0, 'reviewCommentCount': 0, 'noteCount': 479, 'bookmarkCount': 1, 'sort': 1730269738}, {'bookId': '3300032959', 'book': {'bookId': '3300032959', 'title': '顾家北手把手教你雅思词伙', 'author': '顾家北', 'cover': 'https://cdn.weread.qq.com/weread/cover/63/cpPlatform_gsX9swv2QW2jy9FqFwf1YC/s_cpPlatform_gsX9swv2QW2jy9FqFwf1YC.jpg', 'version': 1871575872, 'format': 'epub', 'type': 0, 'price': 22.5, 'originalPrice': 0, 'soldout': 0, 'bookStatus': 1, 'payType': 1048577, 'centPrice': 2250, 'finished': 1, 'free': 0, 'mcardDiscount': 0, 'ispub': 1, 'extra_type': 5, 'cpid': -3382183, 'publishTime': '2016-08-04 00:00:00', 'categories': [{'categoryId': 1400000, 'subCategoryId': 1400005, 'categoryType': 0, 'title': '教育学习-外语'}], 'hasLecture': 0, 'lastChapterIdx': 39, 'paperBook': {'skuId': ''}, 'copyrightChapterUids': [2], 'blockSaveImg': 0, 'language': 'zh', 'hideUpdateTime': False, 'isEPUBComics': 0, 'webBookControl': 0, 'selfProduceIncentive': False}, 'reviewCount': 1, 'reviewLikeCount': 0, 'reviewCommentCount': 0, 'noteCount': 11, 'bookmarkCount': 0, 'sort': 1729905526}, {'bookId': '840978', 'book': {'bookId': '840978', 'title': 'Java核心技术·卷Ⅰ：基础知识（原书第10版）', 'author': '凯S.霍斯特曼', 'translator': '周立新,陈波,叶乃文,邝劲筠,杜永萍', 'cover': 'https://wfqqreader-1252317822.image.myqcloud.com/cover/978/840978/s_840978.jpg', 'version': 1406211751, 'format': 'epub', 'type': 0, 'price': 40.0, 'originalPrice': 0, 'soldout': 0, 'bookStatus': 1, 'payType': 1048577, 'centPrice': 4000, 'finished': 1, 'free': 0, 'mcardDiscount': 0, 'ispub': 1, 'extra_type': 1, 'cpid': 4157477, 'publishTime': '2016-09-01 00:00:00', 'categories': [{'categoryId': 700000, 'subCategoryId': 700003, 'categoryType': 0, 'title': '计算机-计算机综合'}], 'hasLecture': 0, 'lastChapterIdx': 34, 'paperBook': {'skuId': '12037418'}, 'copyrightChapterUids': [2], 'blockSaveImg': 0, 'language': 'zh', 'hideUpdateTime': False, 'isEPUBComics': 0, 'webBookControl': 0, 'selfProduceIncentive': False}, 'reviewCount': 0, 'reviewLikeCount': 0, 'reviewCommentCount': 0, 'noteCount': 1, 'bookmarkCount': 0, 'sort': 1729900784}, {'bookId': '861132', 'book': {'bookId': '861132', 'title': '加拿大一本就Go', 'author': '《环球旅行》编辑部', 'cover': 'https://wfqqreader-1252317822.image.myqcloud.com/cover/132/861132/s_861132.jpg', 'version': 746723889, 'format': 'epub', 'type': 0, 'price': 11.7, 'originalPrice': 0, 'soldout': 0, 'bookStatus': 1, 'payType': 1048577, 'centPrice': 1170, 'finished': 1, 'free': 0, 'mcardDiscount': 0, 'ispub': 1, 'extra_type': 1, 'cpid': 5666835, 'publishTime': '2013-05-01 00:00:00', 'categories': [{'categoryId': 1600000, 'subCategoryId': 1600002, 'categoryType': 0, 'title': '生活百科-旅游'}], 'hasLecture': 0, 'lastChapterIdx': 20, 'paperBook': {'skuId': ''}, 'copyrightChapterUids': [2], 'blockSaveImg': 0, 'language': 'zh', 'hideUpdateTime': False, 'isEPUBComics': 0, 'webBookControl': 0, 'selfProduceIncentive': False}, 'reviewCount': 0, 'reviewLikeCount': 0, 'reviewCommentCount': 0, 'noteCount': 2, 'bookmarkCount': 0, 'sort': 1729900554}, {'bookId': 'CB_EER5RP5S1FSN6rj6sw3AQBjF', 'book': {'bookId': 'CB_EER5RP5S1FSN6rj6sw3AQBjF', 'title': '一个视频说清整个英语语法体系(重塑你的语法认知框架) (1)', 'author': '', 'cover': 'https://weread-1258476243.file.myqcloud.com/app/assets/bookcover/book_cover_default_imported_05.png', 'version': 1683657907, 'format': 'epub', 'type': 0, 'price': 0, 'originalPrice': 0, 'soldout': 0, 'bookStatus': 1, 'payType': 33, 'centPrice': 0, 'finished': 1, 'free': 1, 'mcardDiscount': 0, 'ispub': 0, 'cpid': 0, 'publishTime': '', 'hasLecture': 0, 'lastChapterIdx': 2, 'paperBook': {'skuId': ''}, 'copyrightChapterUids': [], 'limitShareChat': 0, 'blockSaveImg': 0, 'language': 'zh-wr', 'hideUpdateTime': False, 'isEPUBComics': 0, 'webBookControl': 0, 'selfProduceIncentive': False}, 'reviewCount': 0, 'reviewLikeCount': 0, 'reviewCommentCount': 0, 'noteCount': 0, 'bookmarkCount': 1, 'sort': 1729868577}, {'bookId': 'CB_937DuXDsKFei6rg6sw1bIBjN', 'book': {'bookId': 'CB_937DuXDsKFei6rg6sw1bIBjN', 'title': '四级单词', 'author': '', 'cover': 'https://res.weread.qq.com/wrepub/CB_937DuXDsKFei6rg6sw1bIBjN_parsecover', 'version': 0, 'format': 'pdf', 'type': 11, 'price': 0, 'originalPrice': 0, 'soldout': 0, 'bookStatus': 2, 'payType': 33, 'centPrice': 0, 'finished': 1, 'free': 1, 'mcardDiscount': 0, 'ispub': 0, 'cpid': 0, 'publishTime': '', 'hasLecture': 0, 'lastChapterIdx': 102, 'paperBook': {'skuId': ''}, 'otherType': [{'type': 'epub', 'showType': True}], 'showPdf2Epub': True, 'copyrightChapterUids': [], 'limitShareChat': 0, 'blockSaveImg': 0, 'language': 'zh-wr', 'hideUpdateTime': False, 'isEPUBComics': 0, 'webBookControl': 0, 'selfProduceIncentive': False}, 'reviewCount': 0, 'reviewLikeCount': 0, 'reviewCommentCount': 0, 'noteCount': 0, 'bookmarkCount': 1, 'sort': 1729817172}, {'bookId': 'CB_9mi8S88SAFBn6rf6swGvm1zx', 'book': {'bookId': 'CB_9mi8S88SAFBn6rf6swGvm1zx', 'title': '耕伟听力', 'author': '', 'cover': 'https://res.weread.qq.com/wrepub/CB_9mi8S88SAFBn6rf6swGvm1zx_parsecover', 'version': 0, 'format': 'pdf', 'type': 11, 'price': 0, 'originalPrice': 0, 'soldout': 0, 'bookStatus': 2, 'payType': 33, 'centPrice': 0, 'finished': 1, 'free': 1, 'mcardDiscount': 0, 'ispub': 0, 'cpid': 0, 'publishTime': '', 'hasLecture': 0, 'lastChapterIdx': 7, 'paperBook': {'skuId': ''}, 'otherType': [{'type': 'epub', 'showType': False}], 'showPdf2Epub': True, 'copyrightChapterUids': [], 'limitShareChat': 0, 'blockSaveImg': 0, 'language': 'zh-wr', 'hideUpdateTime': False, 'isEPUBComics': 0, 'webBookControl': 0, 'selfProduceIncentive': False}, 'reviewCount': 0, 'reviewLikeCount': 0, 'reviewCommentCount': 0, 'noteCount': 4, 'bookmarkCount': 2, 'sort': 1729614835}, {'bookId': '912071', 'book': {'bookId': '912071', 'title': '吃掉那只青蛙：博恩·崔西的高效时间管理法则', 'author': '[美]博恩·崔西', 'translator': '王璐', 'cover': 'https://cdn.weread.qq.com/weread/cover/48/yuewen_912071/s_yuewen_9120711721641800.jpg', 'version': 1982230015, 'format': 'epub', 'type': 0, 'price': 20.0, 'originalPrice': 0, 'soldout': 0, 'bookStatus': 1, 'payType': 1048577, 'centPrice': 2000, 'finished': 1, 'free': 0, 'mcardDiscount': 0, 'ispub': 1, 'extra_type': 5, 'cpid': 4157477, 'publishTime': '2017-08-22 00:00:00', 'categories': [{'categoryId': 1000000, 'subCategoryId': 1000005, 'categoryType': 0, 'title': '个人成长-人在职场'}], 'hasLecture': 0, 'lastChapterIdx': 102, 'paperBook': {'skuId': '12990531'}, 'copyrightChapterUids': [52], 'blockSaveImg': 0, 'language': 'zh', 'hideUpdateTime': False, 'isEPUBComics': 0, 'webBookControl': 0, 'selfProduceIncentive': False}, 'reviewCount': 0, 'reviewLikeCount': 0, 'reviewCommentCount': 0, 'noteCount': 0, 'bookmarkCount': 1, 'sort': 1599099506}]}
        books = data.get("books")
        books.sort(key=lambda x: x["sort"])
        return books
    else:
        print(r.text)
    return None


def get_sort():
    """获取database中的最新时间"""
    filter = {"property": "Sort", "number": {"is_not_empty": True}}
    sorts = [
        {
            "property": "Sort",
            "direction": "descending",
        }
    ]
    response = client.databases.query(
        database_id=database_id, filter=filter, sorts=sorts, page_size=1
    )
    if len(response.get("results")) == 1:
        return response.get("results")[0].get("properties").get("Sort").get("number")
    return 0


def  get_children(bookId, chapter, summary, bookmark_list):
    children = []
    grandchild = {}
    if chapter != None :
        # 添加目录
        children.append(get_table_of_contents())
        d = {}
        if bookId.startswith("MP_WXS_"):
            for data in bookmark_list:
                title = data.get("title", "未命名")
                # 针对bookmark_list中含有的reviews的信息
                if title == "未命名" and 'reviewId' in data and 'abstract' in data:
                    title = data['refMpInfo']['title']
                if title not in d:
                    d[title] = []
                d[title].append(data)
        else:
            for data in bookmark_list:
                chapterUid = data.get("chapterUid", 1)
                if chapterUid not in d:
                    d[chapterUid] = []
                d[chapterUid].append(data)

        for key, value in d.items():
            if bookId.startswith("MP_WXS_"):
                children.append(
                    get_heading(
                        1,key
                    )
                )
            else:
                if key in chapter:
                    # 添加章节
                    children.append(
                        get_heading(
                            chapter.get(key).get("level"), chapter.get(key).get("title")
                        )
                    )
            for i in value:
                markText = i.get("markText")
                for j in range(0, len(markText) // 2000 + 1):
                    children.append(
                        get_callout(
                            markText[j * 2000 : (j + 1) * 2000],
                            i.get("style"),
                            i.get("colorStyle"),
                            i.get("reviewId"),
                        )
                    )
                if i.get("abstract") != None and i.get("abstract") != "":
                    quote = get_quote(i.get("abstract"))
                    grandchild[len(children) - 1] = quote

    else:
        # 如果没有章节信息
        for data in bookmark_list:
            markText = data.get("markText")
            for i in range(0, len(markText) // 2000 + 1):
                children.append(
                    get_callout(
                        markText[i * 2000 : (i + 1) * 2000],
                        data.get("style"),
                        data.get("colorStyle"),
                        data.get("reviewId"),
                    )
                )
    if summary != None and len(summary) > 0:
        children.append(get_heading(1, "点评"))
        for i in summary:
            content = i.get("review").get("content")
            for j in range(0, len(content) // 2000 + 1):
                children.append(
                    get_callout(
                        content[j * 2000 : (j + 1) * 2000],
                        i.get("style"),
                        i.get("colorStyle"),
                        i.get("review").get("reviewId"),
                    )
                )
    return children, grandchild


def transform_id(book_id):
    id_length = len(book_id)

    if re.match("^\d*$", book_id):
        ary = []
        for i in range(0, id_length, 9):
            ary.append(format(int(book_id[i : min(i + 9, id_length)]), "x"))
        return "3", ary

    result = ""
    for i in range(id_length):
        result += format(ord(book_id[i]), "x")
    return "4", [result]


def calculate_book_str_id(book_id):
    md5 = hashlib.md5()
    md5.update(book_id.encode("utf-8"))
    digest = md5.hexdigest()
    result = digest[0:3]
    code, transformed_ids = transform_id(book_id)
    result += code + "2" + digest[-2:]

    for i in range(len(transformed_ids)):
        hex_length_str = format(len(transformed_ids[i]), "x")
        if len(hex_length_str) == 1:
            hex_length_str = "0" + hex_length_str

        result += hex_length_str + transformed_ids[i]

        if i < len(transformed_ids) - 1:
            result += "g"

    if len(result) < 20:
        result += digest[0 : 20 - len(result)]

    md5 = hashlib.md5()
    md5.update(result.encode("utf-8"))
    result += md5.hexdigest()[0:3]
    return result


def download_image(url, save_dir="cover"):
    # 确保目录存在，如果不存在则创建
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    # 获取文件名，使用 URL 最后一个 '/' 之后的字符串
    file_name = url.split("/")[-1] + ".jpg"
    save_path = os.path.join(save_dir, file_name)

    # 检查文件是否已经存在，如果存在则不进行下载
    if os.path.exists(save_path):
        print(f"File {file_name} already exists. Skipping download.")
        return save_path

    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(save_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=128):
                file.write(chunk)
        print(f"Image downloaded successfully to {save_path}")
    else:
        print(f"Failed to download image. Status code: {response.status_code}")
    return save_path


def try_get_cloud_cookie(url, id, password):
    if url.endswith("/"):
        url = url[:-1]
    req_url = f"{url}/get/{id}"
    data = {"password": password}
    result = None
    response = requests.post(req_url, data=data)
    if response.status_code == 200:
        data = response.json()
        cookie_data = data.get("cookie_data")
        if cookie_data and "weread.qq.com" in cookie_data:
            cookies = cookie_data["weread.qq.com"]
            cookie_str = "; ".join(
                [f"{cookie['name']}={cookie['value']}" for cookie in cookies]
            )
            result = cookie_str
    return result


def get_cookie():
    url = os.getenv("CC_URL")
    if not url:
        url = "https://cookiecloud.malinkang.com/"
    id = os.getenv("CC_ID")
    password = os.getenv("CC_PASSWORD")
    cookie = os.getenv("WEREAD_COOKIE")
    if url and id and password:
        cookie = try_get_cloud_cookie(url, id, password)
    if not cookie or not cookie.strip():
        raise Exception("没有找到cookie，请按照文档填写cookie")
    return cookie
    


def extract_page_id():
    url = os.getenv("NOTION_PAGE")
    if not url:
        url = os.getenv("NOTION_DATABASE_ID")
    if not url:
        raise Exception("没有找到NOTION_PAGE，请按照文档填写")
    # 正则表达式匹配 32 个字符的 Notion page_id
    match = re.search(
        r"([a-f0-9]{32}|[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})",
        url,
    )
    if match:
        return match.group(0)
    else:
        raise Exception(f"获取NotionID失败，请检查输入的Url是否正确")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    options = parser.parse_args()
    weread_cookie = get_cookie()
    database_id = extract_page_id()
    notion_token = os.getenv("NOTION_TOKEN")
    # weread_cookie = 'wr_skey=OQAcd3hU; wr_avatar=https%3A%2F%2Fthirdwx.qlogo.cn%2Fmmopen%2Fvi_32%2F10XeqlPOeeribSpBL8sDoLIuSjWjSGshTbtywGRU0xSotMygbrO6Md7YYIe8icBkB38oibGZdics8cQM7Kv818OT5QmLOgKcNibACicoeKiaQFe8Kk%2F132; wr_fp=348316011; wr_gender=1; wr_localvid=ea73244071f38c62ea73a56; wr_name=Cake; wr_gid=285755748; wr_pf=NaN; wr_rt=web%40K0mPBop5G~j4UFE5JZf_AL; wr_vid=32738402; qq_domain_video_guid_verify=7313f6af9d177308'
    # database_id = ''
    # notion_token = ''
    session = requests.Session()
    session.cookies = parse_cookie_string(weread_cookie)
    client = Client(auth=notion_token, log_level=logging.ERROR)
    session.get(WEREAD_URL)
    latest_sort = get_sort()
    books = get_notebooklist()
    if books != None:
        for index, book in enumerate(books):
            sort = book["sort"]
            if sort <= latest_sort:
                continue
            book = book.get("book")
            title = book.get("title")
            cover = book.get("cover").replace("/s_", "/t7_")
            # print(cover)
            # if book.get("author") == "公众号" and book.get("cover").endswith("/0"):
            #     cover += ".jpg"
            # if cover.startswith("http") and not cover.endswith(".jpg"):
            #     path = download_image(cover)
            #     cover = f"https://raw.githubusercontent.com/{os.getenv('REPOSITORY')}/{os.getenv('REF').split('/')[-1]}/{path}"
            bookId = book.get("bookId")
            author = book.get("author")
            categories = book.get("categories")
            if categories != None:
                categories = [x["title"] for x in categories]
            print(f"正在同步 {title} ,一共{len(books)}本，当前是第{index+1}本。")
            check(bookId)
            isbn, rating = get_bookinfo(bookId)
            id = insert_to_notion(
                title, bookId, cover, sort, author, isbn, rating, categories
            )
            chapter = get_chapter_info(bookId)
            bookmark_list = get_bookmark_list(bookId)
            summary, reviews = get_review_list(bookId)
            bookmark_list.extend(reviews)
            bookmark_list = sorted(
                bookmark_list,
                key=lambda x: (
                    x.get("chapterUid", 1),
                    (
                        0
                        if (
                            x.get("range", "") == ""
                            or x.get("range").split("-")[0] == ""
                        )
                        else int(x.get("range").split("-")[0])
                    ),
                ),
            )
            children, grandchild = get_children(bookId, chapter, summary, bookmark_list)
            results = add_children(id, children)
            if len(grandchild) > 0 and results != None:
                add_grandchild(grandchild, results)

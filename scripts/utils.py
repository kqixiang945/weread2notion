import json
def get_heading(level, content):
    if level == 1:
        heading = "heading_1"
    elif level == 2:
        heading = "heading_2"
    else:
        heading = "heading_3"
    return {
        "type": heading,
        heading: {
            "rich_text": [
                {
                    "type": "text",
                    "text": {
                        "content": content,
                    },
                }
            ],
            "color": "default",
            "is_toggleable": False,
        },
    }


def get_table_of_contents():
    """获取目录"""
    return {"type": "table_of_contents", "table_of_contents": {"color": "default"}}


def get_title(content):
    return {"title": [{"type": "text", "text": {"content": content}}]}


def get_rich_text(content):
    return {"rich_text": [{"type": "text", "text": {"content": content}}]}


def get_url(url):
    return {"url": url}


def get_file(url):
    return {"files": [{"type": "external", "name": "Cover", "external": {"url": url}}]}


def get_multi_select(names):
    return {"multi_select": [{"name": name} for name in names]}


def get_date(start):
    return {
        "date": {
            "start": start,
            "time_zone": "Asia/Shanghai",
        }
    }


def get_icon(url):
    return {"type": "external", "external": {"url": url}}


def get_select(name):
    return {"select": {"name": name}}


def get_number(number):
    return {"number": number}


def get_quote(content):
    return {
        "type": "quote",
        "quote": {
            "rich_text": [
                {
                    "type": "text",
                    "text": {"content": content},
                }
            ],
            "color": "default",
        },
    }


def get_callout(content, style, colorStyle, reviewId):
    # 根据不同的划线样式设置不同的emoji 直线type=0 背景颜色是1 波浪线是2
    emoji = "〰️"
    if style == 0:
        emoji = "💡"
    elif style == 1:
        emoji = "⭐"
    # 如果reviewId不是空说明是笔记
    if reviewId != None:
        emoji = "✍️"
    color = "default"
    # 根据划线颜色设置文字的颜色
    if colorStyle == 1:
        color = "red"
    elif colorStyle == 2:
        color = "purple"
    elif colorStyle == 3:
        color = "blue"
    elif colorStyle == 4:
        color = "green"
    elif colorStyle == 5:
        color = "yellow"
    return {
        "type": "callout",
        "callout": {
            "rich_text": [
                {
                    "type": "text",
                    "text": {
                        "content": content,
                    },
                }
            ],
            "icon": {"emoji": emoji},
            "color": color,
        },
    }


# if __name__ == "__main__":
#     data = '''
# {
#   "synckey": 1731849521,
#   "updated": [
#     {
#       "bookId": "MP_WXS_3079395914",
#       "style": 0,
#       "bookmarkId": "MP_WXS_3079395914_O-ou-GeV4jWwNOwHPDQkZQ_1733-1792",
#       "bookVersion": 0,
#       "range": "1733-1792",
#       "markText": "以杭州的人口和经济体量，每月成交量超过6000套就是及格线，8000套以上算是良好水平，超过10000套则是优秀水平。",
#       "colorStyle": 0,
#       "type": 1,
#       "createTime": 1731849521,
#       "refMpReviewId": "MP_WXS_3079395914_O-ou-GeV4jWwNOwHPDQkZQ"
#     },
#     {
#       "bookId": "MP_WXS_3079395914",
#       "style": 0,
#       "bookmarkId": "MP_WXS_3079395914_O-ou-GeV4jWwNOwHPDQkZQ_1676-1709",
#       "bookVersion": 0,
#       "range": "1676-1709",
#       "markText": "二手房价格真正意义上的上涨，需要成交量维持在一定的水平，有量才有价",
#       "colorStyle": 0,
#       "type": 1,
#       "createTime": 1731848507,
#       "refMpReviewId": "MP_WXS_3079395914_O-ou-GeV4jWwNOwHPDQkZQ"
#     }
#   ],
#   "removed": [],
#   "chapters": [],
#   "book": {
#     "bookId": "MP_WXS_3079395914",
#     "version": 0,
#     "format": "epub",
#     "soldout": 0,
#     "bookStatus": 2,
#     "cover": "http://rescdn.qqmail.com/weread/cover/0/0/t8_0.jpg",
#     "title": "吴晓波频道",
#     "author": "公众号",
#     "coverBoxInfo": {}
#   },
#   "refMpInfos": [
#     {
#       "reviewId": "MP_WXS_3079395914_9B4J96Jkv1~sjbCl~AdoKg",
#       "title": "《问政山东》里的另一个山东",
#       "pic_url": "https://mmbiz.qpic.cn/mmbiz_jpg/pmBoItic0ByhBcQHvseoRRRDw4icEbovmZbg1GHXzJgngREXUgZJe0c5gaFYXWBmmEQRlwzR2T0hEp5YmyMBhiaGg/0?wx_fmt=jpeg",
#       "createTime": 1730217656
#     },
#     {
#       "reviewId": "MP_WXS_3079395914_O-ou-GeV4jWwNOwHPDQkZQ",
#       "title": "二手房拐点来了吗？",
#       "pic_url": "https://mmbiz.qpic.cn/mmbiz_jpg/pmBoItic0Byjjtn3ljtwQm13SQhiaicsKgPz0nAAhcyOCyHjkcMwlvsX8L6fhibs4RSJEnMwVEzDwMMTQam5icEDWvw/0?wx_fmt=jpeg",
#       "createTime": 1731775599
#     }
#   ]
# }
# '''
#
# # 解析 JSON 数据
# r = json.loads(data)
#
# # 提取 updated 列表和 refMpInfos 列表
# updated = r.get("updated", [])
# refMpInfos = {info["reviewId"]: info["title"] for info in r.get("refMpInfos", [])}
#
# # 添加对应的 title
# for item in updated:
#     refMpReviewId = item.get("refMpReviewId")
#     item["title"] = refMpInfos.get(refMpReviewId, "")
#
# # 返回的结果
# result = updated
# print(json.dumps(result, ensure_ascii=False, indent=2))
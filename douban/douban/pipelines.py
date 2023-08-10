# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import redis,pymysql,json
import pandas as pd

class DoubanPipeline:
    def process_item(self, item, spider):
        return item
    def close_spider(self,spider):
        # 所有页面爬取结束后，执行数据持久化，读取redis数据，将其保存到csv文件，和mysql数据库各一份
        # 1.读取redis数据
        r=redis.Redis(host='localhost',port=6379,db=0)
        # 数据在redis数据库中是以list形式保存的，将其全部取出
        datas=r.lrange('doub:items',0,-1)

        # 2.保存到mysql数据库
        m=pymysql.connect(host='127.0.0.1',port=3306,db='douban',user='root',password='1')
        cursor=m.cursor()
        sql='insert into doub(title,director,score,quote,detail)values(%s,%s,%s,%s,%s)'
        for data in datas:
            data2json=json.loads(data)
            cursor.execute(sql,(data2json['title'],data2json['director'],data2json['score'],data2json['quote'],data2json['detail']))
        m.commit()
        m.close()

        # 3.保存到csv文件
        # 转换成dict
        data2json=[json.loads(data) for data in datas]
        df=pd.DataFrame.from_records(data2json)
        df.to_csv('douban.csv',index=False)
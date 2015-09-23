# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
 
import scrapy
from scrapy.contrib.pipeline.images import ImagesPipeline
from scrapy.exceptions import DropItem
from scrapy.http import Request
from settings import *
import pymongo

class WooyunPipeline(object):
    def __init__(self):
        self.__db_connection = pymongo.MongoClient(DB_HOST,DB_PORT)
        self.__db_database = self.__db_connection[DB_DATABASE]
        #self.__db_database.authenticate('wooyun','wooyun')
        self.__db_collection = self.__db_database[DB_COLLECTION]

    def close_spider(self,spider):
        self.__db_connection.close()


    def process_item(self, item, spider):
        
        item['html'] = item['html'].replace("/css/style.css?v=201501291909",LOCAL_CSS_PATH).replace("https://static.wooyun.org/static/js/jquery-1.4.2.min.js", LOCAL_JS_PATH)
        if item['images']:                                              
            for img_pos in item['images']:
                item['html'] = item['html'].replace(img_pos['url'],LOCAL_IMAGES_STORE + img_pos['path'])
       
        filename = LOCAL_HTML_STORE + item['bug_id'] + '.html'
        with open(filename,'w') as f:
        	f.write(item['html'])

        post = {
            "bug_title" : item['bug_title'],
            "open_date" : item['open_date'],
            "bug_type" : item['bug_type'],
            "bug_id" : item['bug_id'],
            "author" : item['author'],
            "html" : "{{url_for('static',filename='wooyun_res/htmls/"+ item['bug_id'] +".html')}}"
        }
        self.__db_collection.insert(post)
        
        return item



class WooyunImagesPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        for image_url in item['image_urls']:
            yield Request(image_url)

    def item_completed(self,results,item,info):
        image_paths = [x['path'] for ok, x in results if ok]
        if not image_paths:
            raise DropItem("Item contains no images")
        item['image_paths'] = image_paths
        #print image_paths
        return item

import logging
from werkzeug import exceptions
from elasticsearch import Elasticsearch

from src.config import AnalysitaConfig


class ElasticHelper:
    CLIENT = None
    USERNAME = AnalysitaConfig.ELASTIC_USERNAME
    PASSWORD = AnalysitaConfig.ELASTIC_PASSWORD
    HOST = AnalysitaConfig.ELASTIC_HOST

    MAPPING = {
        "properties": {
           "content": {
              "type": "text",
              "analyzer": "english"
           },
           "category": {
              "type": "text",
              "analyzer": "english",
              "fields": {
                 "raw": {
                    "type": "keyword"
                 }
              }
           }
        }
    }

    MLT_QUERY = {
        "query": {
           "more_like_this": {
              "fields": [
                 "content",
                 "category"
              ],
              "like": "The apple tree (Malus pumila, commonly and erroneously called Malus domestica) is a deciduous"
                      "tree in the rose family best known for its sweet, pomaceous fruit, the apple. It is cultivated"
                      "worldwide as a fruit tree, and is the most widely grown species in the genus Malus. The tree"
                      "originated in Central Asia, where its wild ancestor, Malus sieversii, is still found today."
                      "Apples have been grown for thousands of years in Asia and Europe, and were brought to North"
                      "America by European colonists. Apples have religious and mythological significance in many"
                      "cultures, including Norse, Greek and European Christian traditions.",
              "min_term_freq": 1,
              "max_query_terms": 20
           }
        }
    }

    @staticmethod
    def get_mlt_query(fields, like):
        MLT_QUERY = {
            "query": {
                "more_like_this": {
                    "fields": [
                        *fields
                    ],
                    "like": like,
                    "min_term_freq": 1,
                    "max_query_terms": 20
                }
            }
        }
        return MLT_QUERY

    def load_data(self):
        self.client.indices.create(index="classification", ignore=[400, 404])
        doc = {
            "category": "Apple (Company)",
            "content": """Apple is an American multinational technology company headquartered in Cupertino, California,
                that designs, develops, and sells consumer electronics, computer software, and online services. Its hardware produc
                ts include the iPhone smartphone, the iPad tablet computer, the Mac personal computer, the iPod portable media p
                layer, the Apple Watch smartwatch, and the Apple TV digital media player. Apple's consumer software includes the
                macOS and iOS operating systems, the iTunes media player, the Safari web browser, and the iLife and iWork creat
                ivity and productivity suites. Its online services include the iTunes Store, the iOS App Store and Mac App Store
                , Apple Music, and iCloud."""
              }
        for i in range(1, 100):
            self.client.index(index="classification", id=i, document=doc)

    @property
    def client(self):
        if self.CLIENT:
            return self.CLIENT
        try:
            self.CLIENT = Elasticsearch(self.HOST, basic_auth=(self.USERNAME, self.PASSWORD))
        except Exception as error:
            logging.exception(f"error: {error}")
            raise exceptions.BadRequest({
                "message": "elastic not found.",
                "status": "failed"
            })
        return self.CLIENT

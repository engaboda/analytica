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

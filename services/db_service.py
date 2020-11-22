import logging
import sqlalchemy
from threading import Lock

#from configs import (MYSQL_USERNAME,
#                    MYSQL_PASSWORD,
#                    MYSQL_DB_NAME,
#                    MYSQL_SMS_DATA_INSTANCE_IP)


class DbService:

    __instance = None
    connection_object = None
    lock = Lock()

    @staticmethod
    def get_instance():
        """ Static access method. """
        logging.debug("singletoninstance %s", DbService.__instance)
        if DbService.__instance == None:
            logging.debug("creating singleton DB instance")
            DbService()

        return DbService.__instance

    def __init__(self):
        DbService.lock.acquire()
        """ Virtually private constructor. """
        if DbService.__instance != None:
            pass
        else:
            self.set_connection_object()
            DbService.__instance = self
        DbService.lock.release()

    def set_connection_object(self):
        """sets a db connection object"""
        connection_object = self.create_db_connection()
        self.connection_object = connection_object

    def create_db_connection(self):
        logging.info("Creating db connection")
        db_conn_url = 'postgresql+psycopg2://postgres:password@ec2-54-166-244-69.compute-1.amazonaws.com/books'
        connection_object = sqlalchemy.create_engine(db_conn_url)
        logging.info("Created db connection")
        return connection_object

    @classmethod
    def execute_query(cls, query):
        db_instance = cls.get_instance()
        db_connection_obj = db_instance.connection_object
        stmt = sqlalchemy.text(query)
        retry = 0
        while retry < 2:
            try:
                with db_connection_obj.connect() as conn:
                    return conn.execute(stmt)
            except Exception as error:
                #print('Error in getting data for mobile number: {} - {}'.format(mobile_number, error))
                retry += 1
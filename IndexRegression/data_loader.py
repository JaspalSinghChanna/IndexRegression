# purpose of this script is to download data FOR THIS TOOL ONLY
# get tickers from csv. combine with tickers for indexes. download close data
import pandas as pd
import yfinance as yf
from pymongo import MongoClient
import logging
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os
import datetime

INDEX_TICKERS = ['^GSPC','^RUT','^NDX']

class MongoDBConnection:
    def __init__(self, env_var = 'MONGO0'):
        pwd = os.getenv(env_var)
        uri = f"mongodb+srv://jsc:{pwd}@serverlessinstance0.qecvssp.mongodb.net/?retryWrites=true&w=majority"
        self.client = MongoClient(uri, server_api=ServerApi('1'))
        self.ping_db()
        self.db = self.client['IndexRegression']
        self.coll = self.db['CloseData']

    def ping_db(self):
        # Send a ping to confirm a successful connection
        try:
            self.client.admin.command('ping')
            print("Pinged your deployment. You successfully connected to MongoDB!")
        except Exception as e:
            raise Exception('Failed to ping Mongo DB') from e
        
class DataDownloader:
    def __init__(self, path='Tickers.csv'):
        self.Mongo = MongoDBConnection()
        self.ticker_df = pd.read_csv(path)

    def get_ticker_list(self):
        tickers = self.ticker_df.Ticker.drop_duplicates().to_list()
        tickers += INDEX_TICKERS
        return tickers

    def download_close_data(self, tickers, start_date=None):
        df1 = yf.download(tickers, threads=True, start=start_date)
        cols = list(df1.columns)
        df2 = df1[[x for x in cols if x[0]=='Close']]
        cols2 = list(df2.columns)
        new_cols = [x[1] for x in cols2]
        df2.columns = new_cols
        return df2

    def insert_into_db(self, df):
        for col in df.columns:
            df1 = df[[col]].rename(columns={col:'Close'}).dropna().reset_index()
            if len(df1) > 0:
                df1['Ticker'] = col
                #df1['Index'] = self.ticker_df.loc[self.ticker_df['Ticker']==col, 'Collection'].to_list()[0]
                records = df1.to_dict("records")
                self.Mongo.coll.insert_many(records)
            else:
                logging.warning(f'No data for {col}')

    def create_indices(self):
        self.Mongo.coll.create_index([('Date'),('Ticker')],name='date_ticker')
        self.Mongo.coll.create_index([('Date')],name='date')
        self.Mongo.coll.create_index([('Ticker')],name='ticker')

    def delete_values(self, start_date=None):
        filter_condition = {}
        if start_date:
            filter_condition['Date'] = {'$gte': start_date}
        logging.info(str(filter_condition))
        self.Mongo.coll.delete_many(filter_condition)


if __name__ == '__main__':
    dd = DataDownloader()
    print(datetime.datetime.now())
    tickers = dd.get_ticker_list()
    print(datetime.datetime.now())
    dd.delete_values()
    print(datetime.datetime.now())
    df = dd.download_close_data(tickers)
    print(datetime.datetime.now())
    dd.insert_into_db(df)
    print(datetime.datetime.now())
    dd.create_indices()
    print(datetime.datetime.now())
# Import required libraries
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from data_loader import MongoDBConnection


class Analytics:
    def __init__(self):
        self.Mongo = MongoDBConnection()
        self.set_ticker_list()

    def set_ticker_list(self):
        tl = []
        for testy in self.Mongo.coll.find().distinct('Ticker'):
            tl.append(testy)
        self.tl = tl

    def get_ticker_records(self, tickers=None):
        if tickers is None:
            self.set_ticker_list()
            tickers = self.tl
        recs = []
        for rec in self.Mongo.coll.find({"Ticker": {"$in":tickers}}):
            recs.append(rec)
        df = pd.DataFrame(recs)[['Date','Close','Ticker']].set_index(['Date','Ticker']).unstack()
        df.columns = [col[1] for col in df.columns]
        return df
        
    def prep_data(self, df):
        df = df.pct_change().dropna()
        return df
    
    def get_contributions(self, df, index):
        X = df.drop(columns=index)
        y = df[index]
        global reg
        reg = LinearRegression().fit(X, y)
        coefs = reg.coef_
        contributions = X*coefs
        predictions = reg.predict(X)
        contributions['Predictions'] = predictions
        final_df = contributions.join(y)
        r2 = self.calculate_r2(reg, X, y)
        weightings = self.create_regression_outputs(X, reg)
        return final_df, reg, r2, weightings
    
    def calculate_r2(self, reg, X, y):
        yhat = reg.predict(X)
        SS_Residual = sum((y-yhat)**2)       
        SS_Total = sum((y-np.mean(y))**2)     
        r_squared = 1 - (float(SS_Residual))/SS_Total
        return r_squared
    
    def create_regression_outputs(self, X, reg):
        df = pd.DataFrame()
        df['Securities'] = list(X.columns)
        df['Weightings'] = reg.coef_
        return df
    
    def find_10_most_important_securities(self, index):
        df = self.get_ticker_records()
        df = self.prep_data(df)
        final_df, reg, r2, weightings = self.get_contributions(df, index)
        weightings = weightings.sort_values('Weightings', ascending=False).head(
            10)[['Securities','Weightings']].to_dict("records")
        print(weightings)

if __name__=='__main__':
    a = Analytics()
    a.find_10_most_important_securities(index='^GSPC')
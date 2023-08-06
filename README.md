# Index Regression
The repo is used to build a GUI that allows you to find how well a basket of securities can explain the performance of a stock index. The analysis is peformed by regressing the daily returns of the index on the daily returns of each security in the basket.

I also have created a function which includes all indices available in the regression, and print the securities with the 10 highest weightings. Due to the large number of explanatory variables (more than 2.5 thousand), this function takes a few minutes to run.


## Set-Up

This tool requires MongoDB to be set-up locally.
The community edition can be installed on Windows by following the instructions here: https://www.mongodb.com/docs/manual/tutorial/install-mongodb-on-windows/#install-mongodb-community-edition

This tool also has dependencies on other python libraries defined in the requirements.txt file. Please ensure these are installed before running.

Once you have installed the relevant dependencies, you can run the data_loader.py file to download data into a local MongoDB.
This will delete any existing data in the collection and download full history.
The functions I created in data_loader.py also allow for updating an existing collection with new data, so please use this for subsequent updates instead of running the whole script.

Once you have downloaded the relevant data, you can run the app.py file.
This creates a plotly dash which can be viewed on port 8053 (http://localhost:8053/).
If you run this from the command line, you should be shown a link to click to access the dash in your browser.

Follow the instructions on the dash to select a basket, review the automated analysis and see how well the basket can explain the performance of the index across the time period chosen. You can also aggregate the daily returns into monthly, quarterly or annual averages to make the graph easier to interpret.
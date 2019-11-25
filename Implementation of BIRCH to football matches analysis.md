# Implementation of BIRCH to football matches analysis 

## Data Set

Match Statistics from top 5 European Leagues

(Italy, England, Spain, France, Germany 2012-2017)

###### data source : https://www.kaggle.com/jangot/ligue1-match-statistics

## plan

1. decide what to analysis and define several key parameters in match data(attempts, possession, tackles, corners etc.).
2. clean and standardise the data.
3. clustering(with BIRCH).
4. analysis the result quantitively and qualitatively.  
5. report.

## Key points

1. decide the angles of analysis and sort out the data frame of target data.
2. build CF trees(clustering feature tree) in python.
3. extract features from clusters.
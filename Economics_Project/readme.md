## Foreword<br>
Before diving into the Economics Project, I helped my former football team by developing a small automation bot for online faxing to book pitches in Hong Kong. It was quite a challenge, as the team admins were neither Python users nor familiar with macOS. Since I didn’t have access to a Windows PC, I spent some time researching how to configure my macOS coding environment so it would work for them. Eventually, I sought help from another ex-teammate, a Windows tech expert, and for the first time, I used GitHub as a collaboration tool. Although I can’t upload the bot due to privacy concerns, I’m pleased to say my ex-teammate was very happy with the result, and I’m grateful for the tech expert's help along the way.
<br>
<br>
<br>
## Getting Started<br>
After completing the bot project, I went back on my data analysis project. However, I initially felt lost trying to decide on a suitable topic. I wasn’t even sure which direction to take. Fortunately, a football teammate here in the UK, who works as a data engineer, suggested that I should explore time series clustering and machine learning. With on online resources I could draw, and my 20 years of work experience, I decided to analyse the relationship between multiple financial markets and yield spread trends.

In economics, we’re taught that the yield spread is a key indicator of how people expect the economy to perform. A positive yield spread, where long-term bond yields are higher than short-term ones, suggests optimism about economic growth (an upward-sloping yield curve). Conversely, a negative yield spread often signals concerns about future economic difficulties.

Stock markets, meanwhile, are thought to reflect expectations of profitability growth. When investors expect companies to become more profitable, they buy shares, driving up stock prices and overall market performance.

By combining these hypotheses, one might assume that yield spread could be a predictor of stock market performance. But is this always the case? Are there exceptions?
<br>
<br>
<br>
## Preparing essential data<br>
To explore this question, I needed extensive daily market data in the past ten years. For yield prices, the U.S. Federal Reserve was my go-to source, as the U.S. Fed rate is widely regarded as the most influential interest rate in the global economy. I chose to use the 10-year and 2-year U.S. government bond yields as the basis for my analysis. To collect the necessary data, I registered with [FRED](https://fred.stlouisfed.org/) , ie the official data source of economic data, to obtain an API key, which I stored in the [/config/general_config.yaml](https://github.com/CharleyYeung/Data_Analysis/blob/main/Economics_Project/config/general_config.yaml) file for data scraping. While I’m unable to share my API key, you can easily register for a free FRED account to access the data yourself.

I was also interested in the global market performance of indices such as the NIKKEI for Japan, the Hang Seng Index for Hong Kong, Shenzhen A Shares for China, and the Taiwan Weighted Index. However, not all of these were available in FRED. To gather data for these markets, I used the Python library [YFinance](https://pypi.org/project/yfinance/), which I implemented in my [/config/scraping_functions.py](https://github.com/CharleyYeung/Data_Analysis/blob/main/Economics_Project/config/scraping_functions.py). Additionally, I listed more tickers for U.S. government bonds with varying maturities in [/config/general_config.yaml](https://github.com/CharleyYeung/Data_Analysis/blob/main/Economics_Project/config/general_config.yaml). Running [/scraping_data.py](https://github.com/CharleyYeung/Data_Analysis/blob/main/Economics_Project/scraping_data.py) allowed me to gather the necessary data, all of which was stored in the [/data/raw/](https://github.com/CharleyYeung/Data_Analysis/tree/main/Economics_Project/data/raw) folder.
<br>
<br>
<br>
## Preprocessing data<br>
Before starting the preprocessing, I combined all the tables for more convenience and better organisable, and saved the result as [/data/raw/all_data_raw.csv](https://github.com/CharleyYeung/Data_Analysis/blob/main/Economics_Project/data/raw/all_data_raw.csv). Although the dates and close prices were sufficient for analysis, the absolute values of prices across markets differed significantly. Therefore, normalization was required. Additionally, the number of data points varied across markets due to differences in trading days and holidays. To align the data set for analysis, I applied trimming, interpolation, and Dynamic Time Warping (DTW) in [/data_preprocessing.py](https://github.com/CharleyYeung/Data_Analysis/blob/main/Economics_Project/data_preprocessing.py). In particular, DTW performs extraordinarily in terms of providing a solid platform for analysis of time-series with temporal distortion. Without its aid, the on-going processes cannot be carried out.

![DTW Matrix Visualization](https://github.com/CharleyYeung/Data_Analysis/blob/main/Economics_Project/data/cleaned/dtw_matrix.png) 
[/data/cleaned/dtw_matrix.png](https://github.com/CharleyYeung/Data_Analysis/blob/main/Economics_Project/data/cleaned/dtw_matrix.png) provides a simplified view of the DTW distance matrix. As shown, the assets are grouped into three general distance ranges.

I was also interested in the global market performance of indices such as the NIKKEI for Japan, the Hang Seng Index for Hong Kong, Shenzhen A Shares for China, and the Taiwan Weighted Index. However, not all of these were available in FRED. To gather data for these markets, I used the Python library YFinance, which I implemented in my scraping_functions.py. Additionally, I listed more tickers for U.S. government bonds with varying maturities in general_config.yaml. Running scraping_data.py allowed me to gather the necessary data, all of which was stored in the /data/raw/ folder.

The DTW Matrix Visualization provides a simplified view of the DTW distance matrix. As shown, the assets are grouped into three general distance ranges.

After completing the DTW preprocessing, I proceeded to cluster the data based on similar behaviour, which allowed for a more structured analysis. Given that asset prices are well-suited for unsupervised learning algorithms, I chose to use K-means clustering from the [tslearn](https://pypi.org/project/tslearn/0.3.0/) library. I also used the silhouette score to evaluate the clustering results. However, before clustering, I needed to define the number of clusters the algorithm should identify.

Since my objective was to compare asset price trends against the yield spread, I required at least two clusters. However, setting the number to just two would provide little insight, as I observed that Chinese markets exhibited very different trends compared to others. Based on the DTW distance matrix, I set the number of clusters between 3 and 7 in [/config/general_config.yaml](https://github.com/CharleyYeung/Data_Analysis/blob/main/Economics_Project/config/general_config.yaml).If you have a different perspective, feel free to adjust these settings as you see fit.

The [/data/cleaned/elbow_plot.png](https://github.com/CharleyYeung/Data_Analysis/blob/main/Economics_Project/data/cleaned/elbow_plot.png): ![Elbow plot](https://github.com/CharleyYeung/Data_Analysis/blob/main/Economics_Project/data/cleaned/elbow_plot.png) indicates that three clusters are optimal for this analysis. Additionally, the [/data/cleaned/silhouette_plot.png](https://github.com/CharleyYeung/Data_Analysis/blob/main/Economics_Project/data/cleaned/silhouette_plot.png) ![Silhouette plot](https://github.com/CharleyYeung/Data_Analysis/blob/main/Economics_Project/data/cleaned/silhouette_plot.png) shows a silhouette score just below 0.6, suggesting a reasonably good clustering result.
<br>
<br>
<br>
## Analysis<br>
I analyzed the clustered time series data in two dimensions in [/analysis.py](https://github.com/CharleyYeung/Data_Analysis/blob/main/Economics_Project/analysis.py). First, I examined the trends by plotting both the individual market trends and the cluster-level trends.
![Asset and Cluster Trends](https://github.com/CharleyYeung/Data_Analysis/blob/main/Economics_Project/data/analysis/asset_and_cluster_trends.png) [/data/analysis/asset_and_cluster_trends.png](https://github.com/CharleyYeung/Data_Analysis/blob/main/Economics_Project/data/analysis/asset_and_cluster_trends.png) illustrates the trends across the markets and clusters we’ve been working on. A similar upward-sloping pattern is evident in the U.S., Japanese, and Taiwanese markets, while the Chinese markets display a mixed direction. The yield spread shows a skewed W-shaped pattern. This aligns with our initial observations and supports the clustering results.

In contrast, [/data/analysis/trend_comparisons.png](https://github.com/CharleyYeung/Data_Analysis/blob/main/Economics_Project/data/analysis/trend_comparisons.png) :
![Trend comparison](https://github.com/CharleyYeung/Data_Analysis/blob/main/Economics_Project/data/analysis/trend_comparisons.png) offers an unexpected insight. In the foreword, I suggested that by combining the hypotheses of the relationship between the yield curve and stock market performance, we might expect stock markets to move in the same direction as the yield curve. However, the trend comparison reveals that U.S. markets actually moved in the opposite direction to the yield curve. Additionally, markets within the same cluster (Cluster 0) exhibit similar behavior.

Surprisingly, markets that were expected to be less positively influenced by the yield curve do not significantly contradict the hypothesis. This raises questions: Could there be time lags affecting the trends? Or are there other underlying factors at play? Further investigation will be required to uncover the answers.
<br>
<br>
<br>
## Prediction<br>
Predictions were generated in [/prediction.py](https://github.com/CharleyYeung/Data_Analysis/blob/main/Economics_Project/prediction.py). Although ARIMA is widely used for forecasting future trends, I adopted LSTM (Long Short-Term Memory) because it places greater emphasis on past events that may influence future outcomes. This assumes market reactions to certain events remain consistent over time. I used [sklearn](https://scikit-learn.org/stable/) and [tensorflow](https://www.tensorflow.org/) to first scale the data to unit variance. Afterward, I initialized and trained the LSTM model with a split of training data from the complete dataset. The model’s evaluation was performed using test data, where mean squared error and R-squared were calculated. Additionally, I assessed the model using mean absolute error, root mean squared error, and mean absolute percentage error (MAPE). These results can be found in [/data/prediction/evaluation.txt](https://github.com/CharleyYeung/Data_Analysis/blob/main/Economics_Project/data/prediction/evaluation.txt) . 

All evaluation metrics suggest excellent predictive performance. While the high R-squared values could raise concerns about overfitting, I cross-validated the same model with other assets, which showed similarly positive results, easing those concerns. The MAPE values indicate that the model's errors are consistently spread across asset price predictions, hinting that the model is not repeating the same types of errors.

Two types of predictive graphs were generated and saved in the [/data/prediction/](https://github.com/CharleyYeung/Data_Analysis/tree/main/Economics_Project/data/prediction) folder. The first type, named 'asset name'_predictions.png, illustrates the comparison between the LSTM predictions and the actual data. It's worth noting that the graphs for clusters look significantly different from individual assets due to scaling differences. The second type, named 'asset'_future_predictions.png, provides actual future performance predictions for the assets. For example, the LSTM model predicts a near-term slump for the SP500, while the Hang Seng Index is projected to continue declining over the next month.

![SP500_future_predictions.png](https://github.com/CharleyYeung/Data_Analysis/blob/main/Economics_Project/data/prediction/SP500_future_predictions.png)
SP500 Prediction.

![HSI_future_predictions.png](https://github.com/CharleyYeung/Data_Analysis/blob/main/Economics_Project/data/prediction/HSI_future_predictions.png)
Hang Seng Index Prediction.
<br>
<br>
<br>
## Afterword<br>
This project has been an incredible learning experience, especially in grasping the complexity of machine learning and its techniques. It also reminded me of the statistical evaluation methods I studied in college.

I want to express my gratitude to my football teammate, Eldon Wong, who provided valuable advice throughout my data analysis journey. He has been like a lighthouse, guiding me whenever I felt lost.

The adventure in data analysis is far from over. I’m enjoying every moment and will continue learning and creating more interesting projects.

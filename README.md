# sporty
A sports analytics project that aims to examine the intuition that the yellow cards of a football game are a factor possible to predict via features describing each team's certain statistics.
Indicatively, we used features shaped from the past three games of each team, such as fouls, yellow cards, ball possession etc. but also referee related features.

The case study of LaLiga Spain.  

## 📝 Workflow
- [Web Scraping](#web_scraping)
- [Data Preprocessing](#data_preprocessing)
- [Dimentionality Reduction](#dimentionality_reduction)
- [Predictive Modeling](#predictive_modeling)

## 🕸️ Web Scraping <a name = "web_scraping"></a>

The data acquisition was conducted through applying web scraping techniques on the famous SofaScore website.  
By using the selenium webdriver we tried to mimic the consecutive clicks a human would follow in order to reach the desired data.

The 4 basic simple steps/clicks are illustrated below:
Not all essential clicks are listed.

**1. Click the button to choose the season of interest**
   
![plot](web-scrapers/screenshots/Screenshot1.png)  
  
**2. Click the season of interest**  
  
![plot](web-scrapers/screenshots/Screenshot2.png)  
  
**3. Click the sort by round button**  

![plot](web-scrapers/screenshots/Screenshot3.png)  
  
**4. Click one after the other the tabs containing the information we thought to relevant**  

![plot](web-scrapers/screenshots/Screenshot4.png)  


The data are stored as csv files.

## 🧹 Data Preprocessing <a name = "data_preprocessing"></a>

Our project was split into two rounds. During the first round we conducted several experiments solely based on the data under the details tab.
Later, during the second round we also combined the available data of statistics tab.  

Due to the two phases explained above, before anything, we performed the necessary part of combining the available data.
More specifically, .. keep from here expaining the available data and their corresponding form

## ✂️ Dimentionality Reduction <a name = "dimentionality_reduction"></a>

We added two option. Factor Analysis / Principal Components Analysis

## 🎯 Predictive Modeling <a name = "predictive_modeling"></a>

We tested rf / lr / xgb ...
gridsearch

Results






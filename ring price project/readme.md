# 💍 Jewelry Price Prediction: An End-to-End Data Pipeline

## 📖 Project Origin: From Study Aid to Data Science
This project began with a practical, personal mission: **supporting my wife's Gemmology exam**. 

Initially, I developed a web scraping program to extract real-world gemstone ring data to create study materials and practice tests for her certification. As the dataset grew, I recognized a unique opportunity to showcase my data engineering skills. I transformed the initial scraper into a full-scale **End-to-End Data Science Project**, bridging the gap between raw web data and predictive machine learning.

> **Note on Privacy & Usage**: To comply with data usage limitations and privacy standards, certain sensitive files (configs, specific URLs, and credential logic) have been excluded. The dataset used in the final analysis has been anonymized.

---

## 🏗️ The Data Pipeline
The project follows a modular, production-grade data engineering workflow:

1.  **Automated Collection**: A Selenium-based scraper navigates authenticated sessions to fetch dynamic jewelry listings from professional platforms.
2.  **Modular Extraction**: A specialized `extractor` module uses **BeautifulSoup4** and **Regex** to transform messy HTML into structured data (extracting carats, dimensions, and alloy types from unstructured text).
3.  **Data Cleaning**: Advanced preprocessing using **Pandas** to handle missing values, feature scaling, and categorical encoding.
4.  **Predictive Modeling**: A regression analysis pipeline that interprets price fluctuations with high accuracy.



---

## 📊 Key Results & Insights
* **Model Performance**: The final regression model achieved an **$R^2$ score of 0.84**, demonstrating that the features extracted successfully explain 84% of the price variance.
* **Feature Importance**: 
    * **Guide Weight** and **Stone Size (Carat)** were identified as the strongest predictors of price.
    * Specific setting styles (e.g., **Six Claw**) and high-grade alloys show a measurable price premium.
* **Stability**: A minimal gap (**0.02**) between Validation and Test $R^2$ indicates a robust model that generalizes well to unseen data.



---

## 🛠️ Tech Stack
- **Automation**: Selenium, WebDriver Manager
- **Parsing**: BeautifulSoup4 (BS4), Regex (Regular Expressions)
- **Data Science**: Pandas, NumPy, Scikit-Learn
- **Visualization**: Matplotlib, Seaborn
- **Excel Engineering**: OpenPyXL (with image-to-cell embedding support)

---

## 📁 Repository Structure
To maintain professional standards, the project is organized into a modular directory:

- `main.py`: The entry point for the scraping and data collection pipeline.
- `modules/`: Reusable logic for web automation (`scraper.py`) and data parsing (`extractor.py`).
- `config/`: (Excluded from Git) Sensitive environment variables and URLs.
- `notebooks/`: `pricing_regression.ipynb` - Exploratory Data Analysis (EDA) and ML modeling.
- `data/`: Segregated into `raw/` and `processed/` folders to ensure data lineage and integrity.

---

## 📈 Competencies Showcase
Through this project, I demonstrated proficiency in:
- **Complex Web Scraping**: Managing session persistence, dynamic content, and anti-detection.
- **Regex for Feature Engineering**: Converting unstructured descriptive text into numerical features for machine learning.
- **Modular Programming**: Writing decoupled, maintainable Python code following DRY (Don't Repeat Yourself) principles.
- **Statistical Interpretation**: Not just building a model, but interpreting **Beta Coefficients** to derive real-world market insights.

---

## ⚙️ Setup & Usage
1.  Clone the repository.
2.  Install dependencies:  
    `pip install -r requirements.txt`
3.  Run the pipeline:  
    `python main.py`
4.  Explore the analysis:  
    Open `notebooks/pricing_regression.ipynb` in a Jupyter environment.
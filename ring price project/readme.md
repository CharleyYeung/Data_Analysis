# Jewelry Price Prediction: An End-to-End Data Pipeline

## Project Overview
This project originated from a real-world application in 2024: assisting my wife's preparation for her **Gemmology certification exam**. Initially, I developed a suite of scripts for **web scraping, data cleaning, and preliminary price analysis** to provide her with comprehensive study materials and market insights. 

Following her successful certification, I decided to refine and professionalize the codebase into a production-grade **Data Engineering and Machine Learning pipeline**. The current iteration features a modular architecture that manages the complete data lifecycle—from raw web extraction to **automated migration from Excel (XLSX) to a structured SQLite database**, all containerized using **Docker** for seamless deployment and reproducibility.

### Privacy and Data Integrity
To comply with data privacy standards and respect source integrity:
* **Excluded Files**: Sensitive configurations, specific URLs, and authentication credentials are excluded from this repository.
* **Pre-populated Database**: A cleaned SQLite database (`jewelry.db`) and a sample Excel file (`ring_details.xlsx`) are included in the Docker image and repository to allow immediate validation of the migration and regression models without requiring live scraping access.
* **Defensive Design**: The system is designed to handle missing configuration files gracefully, allowing the analytical components to function even when the scraper module is inactive.

---

## Data Pipeline Architecture
The project follows a modular, production-grade workflow:

1.  **Automated Collection**: A Selenium-based pipeline managing session persistence and dynamic content navigation.
2.  **Modular Extraction**: A specialized extractor utilizing BeautifulSoup4 and Regular Expressions (Regex) to transform unstructured HTML text into structured numerical features (e.g., carats, dimensions, alloy types).
3.  **Data Migration**: Automated migration scripts that handle data lineage from raw Excel exports to a structured SQL environment.
4.  **Predictive Modeling**: A Scikit-Learn regression pipeline analyzing price variance through feature scaling and categorical encoding.



---

## Technical Performance and Insights
* **Model Accuracy**: The regression model achieved an R-squared ($R^2$) score of 0.84, successfully explaining 84% of price variance.
* **Generalization**: A minimal delta (0.02) between Validation and Test $R^2$ scores indicates high model stability and resistance to overfitting.
* **Predictive Drivers**: Feature importance analysis identified Stone Size (Carat) and Guide Weight as the primary price determinants.

---

## Technology Stack
* **Core Language**: Python 3.12
* **Automation**: Selenium, WebDriver Manager
* **Data Processing**: Pandas, NumPy, BeautifulSoup4, Regex
* **Machine Learning**: Scikit-Learn, Scipy
* **Visualization**: Matplotlib, Seaborn
* **Containerization**: Docker, Docker Compose

---

## Repository Structure
* `main.py`: Entry point for the data collection and migration pipeline.
* `modules/`: Contains `scraper.py`, `extractor.py`, and `database.py` for decoupled logic.
* `notebooks/`: `price_regression.ipynb` for Exploratory Data Analysis (EDA) and ML modeling.
* `data/`: Directory for `jewelry.db` and sample Excel files for demonstration.
* `docker-compose.yml`: Orchestration file for running the pipeline or analysis environments.

---

## Setup and Usage

### Prerequisites
* Docker and Docker Compose installed.
* (Optional) Python 3.12+ for local execution.

### Option 1: Using Docker (Recommended)
The project is containerized to ensure environment consistency.

**Run the Analysis Environment (Jupyter Lab)**
This launches a Jupyter interface to explore the repository structure and run the regression model using the provided database.
```bash
docker-compose up analysis
```

Access via http://localhost:8888 (Token: demo)

Run the Automated Pipeline Note: This requires a valid config/ directory (not provided in the public repo).

```bash
docker-compose run --rm pipeline
```

### Option 2: Local Installation
1.  Install dependencies:
```bash
pip install -r requirements.txt
```

2.  Open notebooks/price_regression.ipynb to view the analysis.

---

## Competencies Demonstrated

Feature Engineering: Utilizing Regex to extract numerical values from unstructured descriptive text.

Defensive Programming: Implementing robust error handling (Try-Except blocks) to allow code execution even when optional configuration modules are absent.

Modular Architecture: Adhering to DRY principles to create maintainable and testable code.

Containerized Deployment: Using Docker orchestration to provide a ready-to-use analytical environment.


---

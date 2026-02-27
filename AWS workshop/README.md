# Cloudy Weather Center (Cloud-Native ETL Project)

An automated weather monitoring dashboard. This project demonstrates a full data pipeline including API data extraction, SQL-based transformation, and cloud-native deployment via Infrastructure as Code (IaC).

## Architecture
- **Data Source**: Open-Meteo API
- **ETL Engine**: Python (Requests, SQLite for transformation)
- **Infrastructure as Code**: Terraform (AWS S3 Static Website Hosting)
- **Frontend**: Vanilla JS and CSS (Responsive design)



## Data Pipeline
1. **Extract**: Python script fetches real-time weather data for 7 global locations (Tokyo, London, Hong Kong, New York, Vancouver, Sydney, and Bangkok).
2. **Transform**: Leverages SQLite to perform data cleaning and categorization. The transformation logic determines the cat's status based on temperature thresholds (e.g., cold climate behavior vs. heat mitigation).
3. **Load**: Formats the processed data into a standardized JSON structure for frontend consumption.
4. **Deploy**: The AWS S3 infrastructure is provisioned and managed via Terraform. Data synchronization is handled through the AWS CLI.

## How to Run

### 1. Execute ETL Pipeline
Ensure you have Python installed, then run the transformation script:
```bash
python etl/transform.py
```

### 2. Provision Infrastructure
Navigate to the terraform directory and apply the configuration:

```bash
cd terraform
terraform init
terraform apply
```

### 3. Deploy Frontend and Data
Synchronize the local source files with your S3 bucket (replace the bucket name with your output):

```bash
aws s3 sync ./src s3://your-unique-bucket-name --exclude ".DS_Store"
```
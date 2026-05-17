provider "aws" {
  region = "eu-west-2" 
}

# Name my Bucket
resource "random_pet" "cloudy_name" {
  length = 2
} 

# Create a S3 Bucket
resource "aws_s3_bucket" "weather_site" {
  bucket = "cloudy-weather-center-${random_pet.cloudy_name.id}"
}

# Configure the Bucket Public Access Mode
resource "aws_s3_bucket_public_access_block" "public_config" {
  bucket = aws_s3_bucket.weather_site.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

# 3. Security Policy
resource "aws_s3_bucket_policy" "allow_public_access" {
  depends_on = [aws_s3_bucket_public_access_block.public_config]
  bucket = aws_s3_bucket.weather_site.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "PublicReadGetObject"
        Effect    = "Allow"
        Principal = "*"
        Action    = "s3:GetObject"
        Resource  = "${aws_s3_bucket.weather_site.arn}/*"
      },
    ]
  })
}

# Toggle on the Static Website Server Mode
resource "aws_s3_bucket_website_configuration" "website" {
  bucket = aws_s3_bucket.weather_site.id

  index_document {
    suffix = "index.html"
  }
}

# Display the url 
output "website_url" {
  value = "http://${aws_s3_bucket.weather_site.bucket_regional_domain_name}/index.html"
}
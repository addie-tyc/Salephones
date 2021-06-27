# Salephones
**A website collects second-hand phone selling information of all brands, dedicated to fairer, healthier
transactions, including user comments of phones and the most importantly, finding you a better price!**
* Crawled second-hand cellphone data from Ptt and Shopee, used Airflow to construct pipeline, built
monitor system with Prometheus and Grafana, and ran on GCP VM.
  - Crawl Ptt mobilesales board every 1 hour and request Shopee search API every 3 hours
  - Create phones catalog from Wiki, use regex to clean data and save data into AWS RDS (MySQL)
  - Use unique key and upsert query to avoid repeated data
  - Obtain comments analysis result from Google NL API and save data into MongoDB
  - Build data pipeline with Airflow by different update frequency to get new case and track sold status
  - Construct Prometheus to get Airflow Statsd log and show metrics on Grafana dashboard
* Developed APIs by Django RESTful, and ran app on AWS EC2
  - Store user related information on AWS RDS (MySQL)
  - Use Nginx as reverse proxy

Website URL: https://salephones.site/home

## Table of Contents
* [Technologies](#Technologies)
* [Architecture](#Architecture)
* [Database Schema](#Database-Schema)
* [Features](#Features)
* [Demo Account](#Demo-Account)
* [Contact](#Contact)

## Technologies

### Back-End
* Django
* RESTful API
* Nginx

### Front-End
* HTML
* CSS
* JavaScript
* Bootstrap
* AJAX

### Database
* MySQL
* MongoDB

### Framework
* MVT (MVC)
  
### Cloud Service
* AWS Elastic Compute Cloud (EC2)
* AWS Relational Database Service (RDS)
* AWS Simple Storage Service (S3)
* GCP VM
* GCP NL API
* GCP CV API

### Networking
* HTTPS
* SSL
* Domain Name System (DNS)

### Test
* Django Test

### Data Source
* [PTT mobilesales](https://www.ptt.cc/bbs/mobilesales/index.html)
* [Shopee](https://shopee.tw/search?keyword=%E4%BA%8C%E6%89%8B%E6%89%8B%E6%A9%9F)

## Architecture
![Architecture](https://aws-bucket-addie.s3.ap-northeast-1.amazonaws.com/smartphone/architecture.png)

## Database Schema
![Database Schema](https://aws-bucket-addie.s3.ap-northeast-1.amazonaws.com/smartphone/schema.png)

## Features
* Home page: all cellphones of different brands  

![home](https://aws-bucket-addie.s3.ap-northeast-1.amazonaws.com/smartphone/home.png)

* Detail page:
  - Price table: show each of sale message
  - Price graph
    - Price history: show the specific phone price history with a new one price and average price with 30 days
    - Different storage price history: show the specific phone price history between different storage
  - Sentiment Score: caculate sentiment score by GCP NL API
  - Comments: use GCP NL API to classify good or bad reviews  

![detail](https://aws-bucket-addie.s3.ap-northeast-1.amazonaws.com/smartphone/detail.png)

* Post a sale / profile page (login required):
  - You can filled form to upload your own sale message
  - Check profile detail and past sale messages  

![sale](https://aws-bucket-addie.s3.ap-northeast-1.amazonaws.com/smartphone/sale.png)
![profile](https://aws-bucket-addie.s3.ap-northeast-1.amazonaws.com/smartphone/profile.png)


## Demo Account
An account is not needed for browsing the phones' information. As of post your own message for sale, signing in is mandatory.
* Account: test
* Password: 0987poiu

## Contact
Tsai-Yun Chung @ addiechung.tyc@gmail.com

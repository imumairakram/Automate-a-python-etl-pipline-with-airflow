# PSX Data Pipeline Using Airflow, Docker, and SQL Server

![Project Architecture](./psx.jpg)

## 📌 Project Overview

This project automates the extraction, transformation, and loading (ETL) of stock market data from the **Pakistan Stock Exchange (PSX)** into a **Microsoft SQL Server** database using the following technologies:

- **Python**: For web scraping and data processing.
- **Apache Airflow**: To orchestrate and schedule ETL tasks.
- **SQLAlchemy**: To interface with the SQL Server database.
- **Docker**: To containerize and manage the entire workflow.

---

## ⚙️ Workflow

1. **Web Scraping**  
   Python scripts scrape stock data from the PSX website.

2. **Data Transformation**  
   The raw data is cleaned and transformed into a structured format using Python.

3. **Load to Database**  
   The transformed data is inserted into a Microsoft SQL Server database using SQLAlchemy.

4. **Orchestration with Airflow**  
   All steps are orchestrated using Airflow DAGs, ensuring automation and scheduling.

5. **Containerization with Docker**  
   Docker containers encapsulate the environment for consistent deployment.

---

## 🛠 Technologies Used

| Tool | Purpose |
|------|---------|
| ![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white) | Scripting and ETL |
| ![Airflow](https://img.shields.io/badge/Apache%20Airflow-017CEE?style=for-the-badge&logo=Apache%20Airflow&logoColor=white) | Task Orchestration |
| ![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-646464?style=for-the-badge&logo=SQLAlchemy&logoColor=white) | Database Connectivity |
| ![SQL Server](https://img.shields.io/badge/Microsoft%20SQL%20Server-CC2927?style=for-the-badge&logo=Microsoft%20SQL%20Server&logoColor=white) | Data Storage |
| ![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=Docker&logoColor=white) | Containerization |

---

## 🚀 How to Run the Project

### Prerequisites

- Docker and Docker Compose
- Python 3.8+
- Microsoft SQL Server (local or remote)

### Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/psx-etl-pipeline.git
   cd psx-etl-pipeline

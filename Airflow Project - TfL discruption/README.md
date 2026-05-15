# TfL Tube Live Status Monitor & Data Pipeline

An end-to-end Data Engineering pipeline designed to orchestrate, ingest, clean, and model real-time London Underground (Tube) status data from the Transport for London (TfL) API. 

This project demonstrates core Data Engineering capabilities including workflow orchestration, data warehousing design (Medallion Architecture), system decoupling, and secure cloud synchronization.

---

##  System Architecture

```text
       [ TfL API ] (External Network)
            │
            ▼ (Every 30 Mins via HttpHook)
   [ Airflow Orchestrator ] (Docker Containers)
            │
            ├──► Task 1: Fetch Raw Data ──► Write to Local Postgres (Raw Table)
            │
            └──► Task 2: Data Cleaning  ──► Process Metadata & Filter 5-Min Delta
                        │
                        ├──► Task 3a: Gold Analytics ──► Create Analytic View (Postgres)
                        │
                        └──► Task 3b: Decoupled Export ──► Format JSON & Sync to AWS S3
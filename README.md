# Roblox Market Intelligence & Trend Pipeline

An executive-level end-to-end data pipeline and Business Intelligence dashboard designed to scrape, transform, analyze, and visualize Roblox game metadata. This project maps keyword saturation against player reach to identify strategic market positioning opportunities ("Viral Niches") and benchmark top-performing game titles.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Power BI](https://img.shields.io/badge/Power_BI-Executive_Dashboard-yellow?logo=powerbi)](visualization/)
[![SQL Server](https://img.shields.io/badge/Database-SQL_Server_(SSMS)-red?logo=microsoftsqlserver)](SQL%20Queries/)

---

## Video Showcase
Watch the executive walkthrough demonstration showcasing both dashboard pages and dynamic DAX filtering:  
[**View Video Showcase on Google Drive**](https://drive.google.com/file/d/1NnTGLfnw9q-kyxFQ7B5vHHvRHSSPhz4w/view?usp=sharing)

---

## Project Overview

Understanding game discoverability and market positioning on Roblox requires bridging high-level search trends with operational title performance. This project automates the extraction of top Roblox game analytics, processes keyword mechanics via SQL Server (SSMS), and delivers an interactive Power BI dashboard for executive decision-making.

### Key Capabilities
- **Automated Scraping & Ingestion:** Python pipeline utilizing `requests` with robust retry handling (`urllib3`) to extract game metrics, titles, player counts, visits, and ratings directly into CSV and SQL Server via `pyodbc`.
- **SQL Analytics Engine:** Custom relational views calculating weighted keyword impact, log impact scores, and dynamic quadrant placements (*Market Dominators*, *Viral Niches*, *Saturated Keywords*, *Niche Noise*).
- **Executive Power BI Dashboard:**
  - **Page 1 (Keyword Impact Matrix):** Maps 3.43K+ keywords against average player reach and surfaces top high-impact mechanics (*build*, *friends*, *earn*, *collect*).
  - **Page 2 (Game-Level Intelligence):** Features a disconnected DAX-based quadrant slicer cross-filtering 237+ game titles, tracking 6.86M+ active players and sentiment metrics in real time.

---

## Repository File Structure

```text
roblox-trend-pipeline/
├── scr/
│   ├── roblox_top_1000_analytics.csv    # Extracted raw game analytics dataset
│   └── scraper.py                       # Python automated web scraper & DB loader
├── SQL Queries/
│   ├── 01_schema.sql                    # Core database table definitions
│   ├── 02_vw_market_impact.sql          # View calculating weighted keyword impact & quadrants
│   ├── 03_vw_games_by_top_keyword_matches.sql # View matching games to strategic keyword quadrants
│   ├── 04_top_games_by_players.sql      # Analytical query for top active player rankings
│   ├── 05_top_keywords_by_impact.sql    # Analytical query ranking keywords by log impact score
│   └── 06_high_efficiency_mechanics.sql # Query isolating high-ROI game mechanics
├── visualization/
│   └── Roblox Intelligence PowerBI.pbix # Interactive executive Power BI report file
├── .gitignore
├── LICENSE                              # MIT License
└── README.md                            # Project documentation
```

---

## Tech Stack & Prerequisites

- **Language:** Python 3.x
- **Python Libraries:** `requests`, `urllib3`, `pyodbc`, `re`, `csv`, `collections`
- **Database Management System:** SQL Server / SQL Server Management Studio (SSMS)
- **Business Intelligence:** Power BI Desktop

---

## Getting Started & Execution

### 1. Data Scraping & Pipeline Execution
Run the automated scraper to fetch real-time Roblox game analytics and load data into SSMS:
```bash
python scr/scraper.py
```
*Note: The pipeline is designed to be executed on-demand (daily or weekly depending on tracking requirements).*

### 2. Database Setup (SSMS)
Execute the SQL scripts in order inside SQL Server Management Studio:
1. Run `01_schema.sql` to initialize database structures.
2. Execute view scripts `02_vw_market_impact.sql` and `03_vw_games_by_top_keyword_matches.sql`.
3. Run analytical scripts `04` through `06` for ad-hoc querying.

### 3. Dashboard Exploration
1. Open `visualization/Roblox Intelligence PowerBI.pbix` in Power BI Desktop.
2. Click **Refresh** in the Home ribbon to pull the latest dataset from your local SQL Server instance.
3. Interact with the **Quadrant Slicer** on Page 2 to explore game-level cohort analysis.

---

## Author & Contact

**Aaron Kane Dungca**  
- **GitHub:** [@KaneD29](https://github.com/KaneD29)  
- **LinkedIn:** [Aaron Kane Dungca](https://www.linkedin.com/in/aaron-kane-dungca/)

---

## AI Use Disclaimer
This project was developed with assistance from generative AI (Gemini) for iterative troubleshooting, DAX optimization, and presentation scripting.
AI tools were strictly utilized as a collaborative thought partner to accelerate code structuring and technical problem-solving.
All database schemas, SQL queries, data validation, dashboard layouts, and core architecture were reviewed, customized, and finalized by the author.
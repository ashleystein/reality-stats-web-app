# reality-stats-web-app

## Project Overview

<!-- A dashboard web application with Reality TV data. -->

## Architecture

<!-- 
Frontend: Made using Dash and Plotly
Backend: ETL pipeline orchestrated using Dagster
Infrastructure: AWS services, ec2, CloudFront, Route 53
-->

## Project Structure

```
RealityStats_Claude/
├── .claude/
│   └── CLAUDE.md
├── .vscode/
│   └── launch.json
├── data/                 
│   ├── analytics_page.csv
│   ├── episode_info.csv
│   ├── insta_latest.csv
│   ├── reality_contestants.csv
│   ├── show_details.csv
│   └── wiki_urls.csv
├── src/
│   ├── app.py                      # Main application entry point
│   ├── aws.py                      # AWS integration
│   ├── config.py                   # Configuration management
│   ├── utils.py                    # Shared utilities
│   └── pages/
│       └── analytics.py            # Analytics page (Dash)
├── pyproject.toml
└── .env
```
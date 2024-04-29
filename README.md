# Exchange Rate Prediction API 

This project serves as the primary API for exchange rate prediction, harnessing the power of a meticulously trained model to deliver precise and reliable forecasts.

## Requirements

>>Python 3.10 or above

>>MySQL 8 or above 

## Setup

1. Clone this repository

```bash
git clone {{repo_url}}
```

2. Navigate to project folder:

```bash
cd exchange-rate-prediction-api
```
3. Create `.env` file:

```bash
cp .env.example .env
```

4. Set DB configuration in `.env` file:

```
DATABASE_HOST=your_host
DATABASE_USER=your_username
DATABASE_PASSWORD=your_password
DATABASE_NAME=your_database_name
```

5. Install project dependency requirements:

```bash
pip install -r requirements.txt
```

6. Run the server:

```bash
flask run --port=your_port
```
# bf1-stats-bot

Telegram bot that pulls Battlefield 1 player stats, weapon breakdowns, vehicle data, and live server info. Planned support for Discord and WhatsApp.

Built on AWS (Lambda for the bot, EC2 for the poller, RDS PostgreSQL for storage). Uses the free [gametools.network](https://api.gametools.network/docs) API as its data source.

## What it does

- `/stats [platform] <player>` returns K/D, SPM, rank, accuracy, skill rating, best class, time played.
- `/weapons [platform] <player>` lists top 10 weapons by kills with accuracy and headshot percentages.
- `/vehicles [platform] <player>` lists top vehicles by kills and vehicles destroyed.
- `/servers [name]` searches active BF1 servers. Without a name, returns the most populated ones.
- `/track [platform] <player>` adds a player to the leaderboard. The poller refreshes their stats every 5 minutes.
- `/leaderboard` ranks tracked players by skill rating.

Platform defaults to `pc`. Options: `pc`, `xbox`, `ps4`.

## Architecture

```
Telegram webhook
      |
  API Gateway (/telegram)
      |
  Lambda (bf1-bot-handler)
      |
  RDS PostgreSQL  <---  EC2 poller (every 60s)
                              |
                    gametools.network API
```

The EC2 instance runs `poller.py` as a systemd service. It polls BF1 servers every 60 seconds and refreshes tracked player stats every 5 minutes, storing everything in PostgreSQL. Lambda handles incoming bot commands and reads from the database. If a player isn't cached yet, Lambda falls back to the API directly.

## Setup

### Prerequisites

- AWS account (free tier covers everything: Lambda, EC2 t3.micro, RDS db.t4g.micro)
- Telegram bot token from [@BotFather](https://t.me/BotFather)

### Database

Create an RDS PostgreSQL instance, then run the schema:

```bash
psql -h <RDS_ENDPOINT> -U bf1admin -d bf1bot -f schema.sql
```

### Lambda

Upload `bf1-bot-lambda-v2.zip` (includes psycopg2). Set these environment variables:

```
TELEGRAM_TOKEN=<your bot token>
DB_HOST=<RDS endpoint>
DB_NAME=bf1bot
DB_USER=bf1admin
DB_PASS=<your password>
```

Set timeout to 15 seconds. Attach the function to your VPC so it can reach RDS.

Create an API Gateway REST API with a POST method on `/telegram` pointing to the Lambda, deploy it, then register the webhook:

```bash
python register_webhook.py <BOT_TOKEN> <API_GATEWAY_URL>/telegram
```

### EC2 Poller

SSH into your instance, install dependencies, set up the environment, and run the poller as a service:

```bash
sudo apt update && sudo apt install -y postgresql-client python3-pip python3-psycopg2

# create env file
cat > /home/admin/.bf1-bot.env << 'EOF'
DB_HOST=<RDS endpoint>
DB_NAME=bf1bot
DB_USER=bf1admin
DB_PASS=<your password>
EOF

# copy poller.py to the instance, then create a systemd service for it
```

## Project structure

```
.
├── src/
│   └── lambda_function.py   # Telegram bot handler (Lambda)
├── poller.py                # Server/player polling daemon (EC2)
├── schema.sql               # PostgreSQL table definitions
├── register_webhook.py      # One-time webhook registration script
└── README.md
```

## Status

Telegram bot is working. Discord and WhatsApp integrations are planned.

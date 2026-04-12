# Infrastructure

## n8n

Default credentials for the local Docker Compose setup:

| Field    | Value                        |
|----------|------------------------------|
| Email    | `insaide-trader@email.com`   |
| Password | `InsA!D3Tr@d3r`              |

## Setting up ngrok with n8n

[ngrok](https://ngrok.com/) exposes the local n8n instance so external webhooks can reach it.

1. Install ngrok
2. Add your auth token:
   ```bash
   ngrok config add-authtoken YOUR_TOKEN_HERE
   ```
3. Start the tunnel:
   ```bash
   ngrok http 5678
   ```
4. Copy the forwarding URL provided by ngrok (e.g. `https://xxxx-xxxx.ngrok-free.dev`) and update `N8N_HOST` and `WEBHOOK_URL` in `docker-compose.yaml`:
   ```yaml
   N8N_HOST=your-subdomain.ngrok-free.dev
   WEBHOOK_URL=https://your-subdomain.ngrok-free.dev/
   ```
5. Restart the n8n container so it picks up the new URL.
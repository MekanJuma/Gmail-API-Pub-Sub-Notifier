# <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/7/7e/Gmail_icon_%282020%29.svg/2560px-Gmail_icon_%282020%29.svg.png" width="30"> Gmail-API-Pub-Sub-Notifier

Okalmadyk Gmail habarlaryňyzy attachment lar bilen göni Discord-a iberiň! Python esasly bu programma, gelýän habarlary diňlemek etmek üçin Gmail API ulanýar we webhooks ulanyp, görkezilen Discord kanalyna iberýär. <img src="https://static.vecteezy.com/system/resources/previews/018/930/718/original/discord-logo-discord-icon-transparent-free-png.png" width="30">

# Features:

-   Real-time email notifications on Discord.
-   Attachment forwarding.
-   Filtered to only send unread emails.

# Pre-requisites:

**Google Cloud Platform (GCP) setup with:**

-   Gmail API enabled.
-   Consent screen created with Gmail scopes.
-   OAuth2 credentials.
-   Pub/Sub enabled.
-   Python (3.7 or newer)

# How does it work?

**GCP Gmail API**: The Gmail API lets the application fetch Gmail mailbox data.

**Google Pub/Sub**: It's a messaging service that allows real-time messaging.

**Topic**: A named resource to which messages are sent by publishers.

**Subscription**: A named resource representing the stream of messages from a single, specific topic.

**Flask Webhook**: Our server listens for incoming messages from GCP and processes them accordingly.

# Setup:

**Google Cloud Platform:**
Follow the instructions in [this guide](https://www.geeksforgeeks.org/how-to-create-a-free-tier-account-on-gcp/) to set up your GCP account and enable the necessary services.

**Local Setup:**

1. Install necessary Python packages:

```
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
pip install flask flask-admin flask-cors
pip install firebase firebase-admin
pip install discord
pip install requests BeautifulSoup4
```

2. Update the configurations:

-   Add your GCP **creds.json**
-   Update the webhook_url variable with your Discord webhook in flask_config.py
-   Update the topic_name variable with your GCP Topic Name in watch_setup.py

3. Run the python file watch_setup.py to start listening to the inbox

```
python watch_setup.py
```

4. Run the python file app.py to start the webhook

```
python watch_setup.py
```

# Usage:

Once set up, the application will:

**Authorize:** Use OAuth2 to authorize and access Gmail data.

**Watch:** It will start watching for unread messages in the mailbox.

**Notify:** On receiving a new unread email, it sends the content, including attachments, to the specified Discord channel.

# Contributions:

Feel free to fork this project, open issues, or submit PRs. All contributions are welcome!

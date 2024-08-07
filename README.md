# Thunderboard Soundboard integration
---
## About
This integration allows you to control the Thunderboard Soundboard Bot from Home Assistant.
---
## Installation
Install this integration by copying the `custom_components/thunderboard_soundboard` folder to your Home Assistant `config/custom_components` folder.
Alternatively, you can install it via HACS by adding this repository to HACS. For this you can add the repository URL `https://github.com/thunderboard-bot/thunderboard-hacs` to HACS.
---
## Configuration
To enable this integration, add the following to your `configuration.yaml` file:

```yaml
thunderboard:
  access_token: "your_access_token_here"
  service_url: "http://example.com"
```

Alternatively, you can configure this integration via the integrations page in the Home Assistant UI, search for "Thunderboard" and follow the instructions.

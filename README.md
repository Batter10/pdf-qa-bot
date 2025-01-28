# PDF QA Bot

Een intelligente chatbot die vragen kan beantwoorden over geüploade PDF documenten.

## Features

- PDF document upload via drag & drop
- Vraag & antwoord functionaliteit
- Document samenvatting
- FAQ generatie
- Document vergelijking

## Installatie

1. Clone de repository:
```bash
git clone https://github.com/Batter10/pdf-qa-bot.git
cd pdf-qa-bot
```

2. Installeer de dependencies:
```bash
pip install -r requirements.txt
```

3. Maak een .env bestand aan en vul je API key in:
```bash
CLAUDE_API_KEY=jouw_api_key_hier
# of
OPENAI_API_KEY=jouw_api_key_hier
```

4. Start de applicatie:
```bash
python app.py
```

## Gebruik

1. Open de applicatie in je browser
2. Upload een PDF document
3. Stel vragen over de inhoud
4. Gebruik de extra functies zoals samenvatten en FAQ generatie

## Tech Stack

- Frontend: HTML, CSS, JavaScript
- Backend: Python met FastAPI
- AI: Claude/OpenAI API
- Vector Database: FAISS/Weaviate
# HotelMate Vyra 2.0

A multi-layered intelligent hotel concierge assistant powered by local knowledge bases and OpenAI GPT integration. Vyra provides hotel guests with immediate, contextual answers about facilities, policies, and local recommendations.

## Overview

HotelMate Vyra 2.0 is a Flask-based web application that routes guest inquiries through a three-tier response pipeline:

1. **Local Knowledge Base** (instant, deterministic answers)
2. **OpenAI GPT** (context-aware AI responses with interaction limits)
3. **Fallback Messages** (graceful degradation)

The system supports multi-language responses and implements session-based interaction tracking to prevent off-topic conversations after 10 interactions.

---

## Architecture

### Core Components

```
main.py                 # Flask application entry point, session management, interaction tracking
├── core/router.py      # Request routing and response orchestration
├── core/brain.py       # Knowledge base matching engine (local answers)
└── core/openai_client.py # OpenAI API wrapper
```

### Data Layer

```
data/
├── hotel_data/hotel_data.json    # Hotel metadata, amenities, contact info
├── hotels/<slug>/knowledge.json  # Hotel-specific FAQ and facts
├── brain.json                    # Legacy fallback knowledge base
└── active_hotel.txt              # Active hotel identifier
```

### Configuration

```
config/
├── hotel_profile.json   # Legacy personality/tone settings
└── setings.yaml         # AI persona and behavioral rules
```

### Frontend

```
templates/index.html     # Web UI template
static/
├── css/style.css       # Styling
└── js/scriptjs         # Client-side logic
```

---

## Key Features

### 1. Multi-Tier Response Pipeline
- **Local First**: Fast, consistent answers from knowledge base
- **AI Fallback**: OpenAI GPT for complex queries with context
- **Graceful Degradation**: User-friendly fallback messages

### 2. Knowledge Base System
- **Facts**: Simple key-value pairs (check-in, check-out, WiFi, parking)
- **FAQ**: Question-answer pairs with multi-language tags
- **Dynamic Loading**: Switch hotels via `active_hotel.txt`

### 3. Session Management
- Interaction counting per guest session
- Off-topic detection after 10 interactions
- Flask session storage with automatic cleanup

### 4. Multi-Language Support
- Romanian, English, German base support
- Extensible tag system in FAQ entries
- Normalized text matching (removes diacritics, handles case variations)

---

## Configuration Parameters

### 1. Flask Application Settings
**File**: [main.py](main.py#L11)

```python
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "vyra_dev_secret_key_change_me")
```
- **FLASK_SECRET_KEY**: Session encryption key (required for production)
- **PORT**: Server port (default: 5000)
- **FLASK_ENV**: Set to "production" for production deployments

**Environment Variables**:
```bash
FLASK_SECRET_KEY=your_secret_key_here
OPENAI_API_KEY=sk-your-openai-key
PORT=5000
```

---

### 2. OpenAI Configuration
**File**: [core/openai_client.py](core/openai_client.py)

```python
response = client.responses.create(
    model="gpt-4.1-mini",              # Model selection
    input=f"You are Vyra, a polite hotel concierge.\nGuest: {message}"
)
```

**Parameters to Modify**:
- **model**: Change from `gpt-4.1-mini` to alternative OpenAI models (e.g., `gpt-4`, `gpt-3.5-turbo`)
- **System Prompt**: Modify concierge personality in the `input` parameter

---

### 3. Interaction Limit
**File**: [core/router.py](core/router.py#L56)

```python
def route_question(user_message: str, interaction_count: int = 0):
    if interaction_count >= 10:
        return "You are off topic", "fallback"
```

**Parameter**:
- **Interaction Limit**: Change `10` to any desired interaction count threshold

**File**: [main.py](main.py#L18-L24)

```python
interaction_count = session.get("interaction_count", 0)
bot_response, response_source = route_question(user_message, interaction_count)
session["interaction_count"] = interaction_count + 1
```

---

### 4. Active Hotel Selection
**File**: [data/active_hotel.txt](data/active_hotel.txt)

```
niu_furth
```

This determines which hotel's knowledge base is loaded. Set to any folder name in `data/hotels/`.

**Default Fallback**: If file doesn't exist, system uses `niu_furth` as DEFAULT_HOTEL_SLUG in [core/brain.py](core/brain.py#L9).

---

### 5. Hotel Data
**File**: [data/hotel_data/hotel_data.json](data/hotel_data/hotel_data.json)

```json
{
  "name": "Melia Grand Hermitage",
  "location": { "address": "...", "city": "..." },
  "contact": { "telefon": "...", "email": "...", "website": "..." },
  "amenities": ["WiFi", "Pool", "Spa", ...],
  "checkin": "14:00",
  "checkout": "12:00",
  "languages_spoken": ["Bulgarian", "English", "Russian", "German"],
  "rating": 4.5,
  "review_count": 1800
}
```

**Configurable Fields**:
- `name`, `location`, `contact`: Hotel metadata
- `amenities`: Array of available facilities
- `checkin`/`checkout`: Times in HH:MM format
- `languages_spoken`: Supported languages
- `rating`, `review_count`: Reviews and ratings

---

### 6. Hotel-Specific Knowledge Base
**File**: [data/hotels/niu_furth/knowledge.json](data/hotels/niu_furth/knowledge.json)

```json
{
  "facts": {
    "checkin": "Check-in starts at 15:00.",
    "checkout": "Check-out is until 12:00.",
    "wifi": "Free high-speed Wi-Fi is available in all rooms.",
    "parking": "On-site parking is available for €8 per day."
  },
  "faq": [
    {
      "q": "What time is breakfast?",
      "a": "Breakfast is available as a buffet and is usually charged separately.",
      "tags": ["breakfast", "mic dejun"]
    }
  ]
}
```

**Facts Schema**:
- Simple key-value pairs for common questions
- Keys must match keywords in [core/brain.py](core/brain.py#L82-L90) fact rules

**FAQ Schema**:
- `q`: Question string
- `a`: Answer string  
- `tags`: Array of searchable keywords (multilingual)

**Adding Keywords**: Modify fact_rules in [core/brain.py](core/brain.py#L82-L90):

```python
fact_rules = [
    (["check in", "checkin", "sosire"], "checkin"),
    (["check out", "checkout", "plecare"], "checkout"),
    (["wifi", "wi fi", "internet"], "wifi"),
    # Add new rules here
]
```

---

### 7. OpenAI Prompt Context
**File**: [core/router.py](core/router.py#L30-L50)

```python
context = f"""
You are Vyra, the digital concierge for {hotel_name}.

Location:
- City: {city}
- Address: {address}

Hotel context (use ONLY this when possible):
- Facilities: {json.dumps(facilities, ensure_ascii=False)}
- Rules: {json.dumps(rules, ensure_ascii=False)}
- FAQ: {json.dumps(faq, ensure_ascii=False)}

Important rules:
1) If the user asks about nearby places (restaurants, attractions), recommend options GENERICALLY...
"""
```

**Modifiable Elements**:
- Persona name: Change "Vyra" to custom name
- System instructions: Modify rules and guidelines
- Context injection: Add/remove hotel_data fields

---

### 8. Text Normalization Rules
**File**: [core/brain.py](core/brain.py#L12-L22)

```python
def _normalize(text: str) -> str:
    text = text.strip().lower()
    # remove diacritics
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    # collapse spaces
    text = re.sub(r"\s+", " ", text)
    return text
```

**Customization Options**:
- Remove `.lower()` for case-sensitive matching
- Modify regex pattern `r"\s+"` for whitespace handling
- Add/remove diacritic normalization for specific languages

---

## Environment Setup

### Prerequisites
- Python 3.8+
- OpenAI API key
- Flask, requests, python-dotenv

### Installation

1. **Clone Repository**
   ```bash
   git clone <repository>
   cd hotelmate-vyra-2.0
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment**
   ```bash
   # Create .env file
   echo "OPENAI_API_KEY=sk-your-key-here" > .env
   echo "FLASK_SECRET_KEY=your-random-secret-here" >> .env
   echo "PORT=5000" >> .env
   ```

4. **Set Active Hotel**
   ```bash
   echo "niu_furth" > data/active_hotel.txt
   ```

5. **Run Application**
   ```bash
   python main.py
   ```

   Access at: `http://localhost:5000`

---

## Development Workflow

### Adding a New Hotel

1. **Create Hotel Directory**
   ```
   data/hotels/my_hotel/
   └── knowledge.json
   ```

2. **Create Hotel Knowledge Base**
   ```json
   {
     "facts": { "checkin": "15:00", ... },
     "faq": [{ "q": "...", "a": "...", "tags": [...] }]
   }
   ```

3. **Switch Active Hotel**
   ```bash
   echo "my_hotel" > data/active_hotel.txt
   ```

### Adding New FAQ Entries

Edit [data/hotels/niu_furth/knowledge.json](data/hotels/niu_furth/knowledge.json):

```json
{
  "q": "Is there a gym?",
  "a": "Yes, our fitness center is open 6am-10pm.",
  "tags": ["gym", "fitness", "exercise", "sport"]
}
```

### Testing Knowledge Base Matching

The matching engine in [core/brain.py](core/brain.py#L73-L102) uses:
- Keyword matching for facts
- Substring and tag-based matching for FAQ
- Normalized text (lowercase, diacritics removed)

Test queries:
- "Check-in" → matches "checkin" fact
- "WiFi" → matches "wifi" fact  
- "Breakfast?" → matches FAQ tag "breakfast"

---

## Response Flow Diagram

```
Guest Message
    ↓
[Interaction Limit Check] ← session["interaction_count"] ≥ 10?
    ↓ (No)
[Local Knowledge Base] ← core/brain.py find_answer()
    ↓ (No local match)
[OpenAI GPT] ← core/openai_client.py ask_openai()
    ↓ (Error/Exception)
[Fallback Message]
    ↓
Response to Guest + Update session["interaction_count"]
```

---

## Troubleshooting

### Empty Response from OpenAI
- Check `OPENAI_API_KEY` in `.env`
- Verify API key has available credits
- Check model name in [core/openai_client.py](core/openai_client.py#L9)

### Questions Not Matching Knowledge Base
- Verify knowledge.json file format in [data/hotels/niu_furth/knowledge.json](data/hotels/niu_furth/knowledge.json)
- Check keywords in [core/brain.py](core/brain.py#L82-L90) fact_rules
- Test normalization logic: spaces, case, diacritics

### Active Hotel Not Loading
- Verify `data/active_hotel.txt` exists and contains valid hotel slug
- Confirm folder exists in `data/hotels/<slug>/`
- Check JSON syntax in knowledge.json

### Session Not Persisting
- Ensure `FLASK_SECRET_KEY` is set in environment
- Check Flask development vs production mode
- Session data stored server-side (Flask default)

---

## API Endpoints

### Web Routes

**GET / POST** `/`
- Main chat interface
- POST: Submit guest message
- GET: Display last exchange
- Session-based interaction tracking

---

## Dependencies

- **Flask**: Web framework
- **python-dotenv**: Environment variable management
- **openai**: OpenAI API client
- **requests**: HTTP library (optional, included)
- **gunicorn**: Production WSGI server

See [requirements.txt](requirements.txt) for versions.

---

## Production Deployment

1. **Set Environment Variables**
   ```bash
   export OPENAI_API_KEY=sk-...
   export FLASK_SECRET_KEY=your-production-secret
   export FLASK_ENV=production
   ```

2. **Run with Gunicorn**
   ```bash
   gunicorn -w 4 -b 0.0.0.0:5000 main:app
   ```

3. **Enable HTTPS** (recommended)
   - Use reverse proxy (nginx, Apache)
   - Configure SSL certificates

4. **Scale Knowledge Base**
   - Move hotel_data.json to database
   - Cache frequently accessed FAQs
   - Consider vector embeddings for semantic matching

---

## Future Enhancements

- [ ] Vector embeddings for semantic FAQ matching
- [ ] Multi-language response generation
- [ ] Guest feedback loop and knowledge base auto-improvement
- [ ] Analytics dashboard for common questions
- [ ] Integration with hotel management systems (PMS)
- [ ] Voice input/output (core/voice/ module)
- [ ] Admin panel for knowledge base management

---

## License

Proprietary - HotelMate Systems

## Contact

For development questions or contributions, contact the development team.

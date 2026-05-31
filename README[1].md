# Live Sports Predictions Demo

Eyi jẹ́ Streamlit app tí ó ń fi live football àti basketball fixtures/games hàn, pẹ̀lú demo prediction columns láti fi UI flow hàn.

## Ohun tí app náà ṣe
- Gba **football fixtures** láti `football-data.org`
- Gba **basketball games** láti `BALldontlie`
- Fi **confidence**, **model edge**, àti **pick** hàn gẹ́gẹ́ bí demo placeholders
- Ṣe fallback sí sample data bí API keys kò bá sí
- Ṣetan fún **Streamlit Community Cloud deployment**

## Fáìlì tó wà nínú repo
- `app.py` — app pàtàkì fún deployment
- `requirements.txt` — dependencies Python
- `.streamlit/config.toml` — config Streamlit
- `.streamlit/secrets.toml.example` — àpẹẹrẹ secrets setup
- `.gitignore` — kí secrets má bàa wọ git

## Bí o ṣe n ṣiṣẹ lọ́dọ̀ọ́rẹ́ (local)
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
streamlit run app.py
```

## Secrets setup
Ṣàtúnṣe `.streamlit/secrets.toml` pẹ̀lú API keys rẹ:

```toml
FOOTBALL_DATA_API_KEY = "your_football_data_key"
BALLDONTLIE_API_KEY = "your_balldontlie_key"
```

App náà tún lè ka environment variables:

```bash
export FOOTBALL_DATA_API_KEY="your_football_data_key"
export BALLDONTLIE_API_KEY="your_balldontlie_key"
streamlit run app.py
```

## Streamlit Community Cloud deployment
1. Fi gbogbo fáìlì sínú GitHub repo rẹ.
2. Lọ sí Streamlit Community Cloud.
3. Tẹ **Create app**.
4. Yàn repo, branch, àti `app.py` gẹ́gẹ́ bí main file.
5. Ní **Advanced settings**, fi secrets yìí sílẹ̀:

```toml
FOOTBALL_DATA_API_KEY = "your_football_data_key"
BALLDONTLIE_API_KEY = "your_balldontlie_key"
```

6. Tẹ **Deploy**.

## Àkíyèsí
- `pick`, `confidence`, àti `model edge` jẹ́ **demo heuristic** ní báyìí.
- Bí o bá fẹ́ production prediction gidi, rọ́pò `demo_pick_for_football()` àti `demo_pick_for_basketball()` pẹ̀lú model prediction rẹ.
- Má ṣe commit `.streamlit/secrets.toml` sí git.

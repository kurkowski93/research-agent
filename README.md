# Deeper Knowledge Agent

Agent badawczy oparty na LangGraph, który pomaga w pogłębianiu wiedzy na wybrany temat.

## Instalacja

1. Sklonuj repozytorium:
```bash
git clone https://github.com/yourusername/deeper-knowledge-agent.git
cd deeper-knowledge-agent
```

2. Zainstaluj zależności:
```bash
cd my-app/my_agent
pip install -r requirements.txt
```

3. Skonfiguruj zmienne środowiskowe w pliku `.env`:
```
OPENAI_API_KEY=your_openai_api_key
TAVILY_API_KEY=your_tavily_api_key
```

## Użycie

```python
from my_agent import graph
from my_agent.utils.state import DeeperKnowledgeSeekerState

# Utwórz stan początkowy
state = DeeperKnowledgeSeekerState(
    profile="Student informatyki zainteresowany sztuczną inteligencją",
    topic_to_research="Transformery w przetwarzaniu języka naturalnego",
    what_is_already_known="Podstawowa wiedza o sieciach neuronowych i uczeniu maszynowym",
    topics_ideas=[],
    deeper_knowledge_results=[]
)

# Uruchom graf
config = {"model_name": "gpt-4o-mini"}
results = graph.invoke(state, config=config)

# Wyświetl wyniki
print(results)
```

## Struktura projektu

```
my-app/
├── my_agent/
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── tools.py
│   │   ├── nodes.py
│   │   └── state.py
│   ├── requirements.txt
│   ├── __init__.py
│   └── agent.py
├── .env
└── langgraph.json
```

## Licencja

MIT
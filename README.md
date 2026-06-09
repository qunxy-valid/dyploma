# Python DevOps Lifecycle API

Навчальний проєкт для курсової роботи на тему автоматизації життєвого циклу програмного забезпечення та забезпечення надійності коду з використанням Python.

Проєкт демонструє:

- REST API на FastAPI;
- демонстраційний web UI для показу роботи системи;
- автоматизовані тести через pytest;
- перевірку стилю та якості коду через ruff;
- статичну перевірку типів через mypy;
- контейнеризацію через Docker;
- CI pipeline через GitHub Actions.

## Структура проєкту

```text
python-devops-lifecycle/
├── .github/workflows/ci.yml
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── schemas.py
│   ├── services.py
│   └── static/
│       ├── app.js
│       ├── index.html
│       └── styles.css
├── tests/
│   └── test_main.py
├── Dockerfile
├── pyproject.toml
└── README.md
```

## Локальний запуск

Створіть та активуйте віртуальне середовище:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Встановіть залежності:

```powershell
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Запустіть API:

```powershell
uvicorn app.main:app --reload
```

Після запуску документація API буде доступна за адресою:

```text
http://127.0.0.1:8000/docs
```

Демонстраційний інтерфейс буде доступний за адресою:

```text
http://127.0.0.1:8000/
```

У ньому можна створювати дефекти якості, закривати їх, запускати демонстраційний pipeline і переглядати приклад коду з pytest-тестами.

## Перевірка якості коду

```powershell
ruff format --check .
ruff check .
mypy app
pytest
```

## Docker

Збірка образу:

```powershell
docker build -t python-devops-lifecycle .
```

Запуск контейнера:

```powershell
docker run --rm -p 8000:8000 python-devops-lifecycle
```

## GitHub Actions

Файл `.github/workflows/ci.yml` автоматично запускає pipeline при `push` або `pull request` у гілку `main`.

Pipeline виконує такі етапи:

1. Завантажує код репозиторію.
2. Встановлює Python 3.11 та 3.12.
3. Встановлює залежності проєкту.
4. Перевіряє форматування коду.
5. Запускає лінтер.
6. Запускає статичну перевірку типів.
7. Запускає автоматизовані тести.
8. Збирає Docker-образ.

Для базового CI не потрібні токени або секрети. Достатньо завантажити проєкт у GitHub-репозиторій, де є гілка `main`, і GitHub Actions запуститься автоматично.

## Приклади запитів

Перевірка стану сервісу:

```powershell
curl http://127.0.0.1:8000/health
```

Створення запису про дефект якості:

```powershell
curl -X POST http://127.0.0.1:8000/issues `
  -H "Content-Type: application/json" `
  -d '{"title":"Missing unit test for payment flow","service":"billing","severity":"high"}'
```

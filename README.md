# mti-mcp

MCP-сервер для личного кабинета LMS МТИ. Сервер использует библиотеку
[`mti-api`](https://github.com/derived-functor/mti-api) для cookie-сессии и
разбора HTML, а наружу предоставляет read-only tools для профиля, расписания,
вебинаров, курсов, успеваемости, финансов, документов, сообщений и уведомлений.

Задайте `MTI_LOGIN` и `MTI_PASSWORD` в окружении или в `.env`. Сам MCP-код не
читает credentials — их обрабатывает `MTIClient.from_env()` из `mti-api`.

### Переменные окружения

Создайте файл `.env` в рабочем каталоге:

```dotenv
MTI_LOGIN=your-login
MTI_PASSWORD=your-password
```

Не добавляйте `.env` и файл сессии в git. При необходимости можно указать
переменные непосредственно перед запуском:

```bash
MTI_LOGIN=your-login MTI_PASSWORD=your-password uv run mti-mcp
```

Дополнительные настройки:

```dotenv
# Файл cookie-сессии
MTI_SESSION_PATH=/home/user/.cache/mti-api/session.pickle

# Адрес LMS, по умолчанию https://lms.mti.moscow
MTI_BASE_URL=https://lms.mti.moscow

# Каталог для скачанных документов и XLSX-экспортов
MTI_DOWNLOAD_DIR=/home/user/Downloads/mti
```

```json
{
  "mcpServers": {
    "mti": { "command": "uv", "args": ["run", "mti-mcp"] }
  }
}
```

```bash
uv sync
uv run mti-mcp
```

Необязательные переменные: `MTI_SESSION_PATH`, `MTI_BASE_URL` и
`MTI_DOWNLOAD_DIR` (каталог для явно запрошенных документов).

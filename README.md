# Claude To-Do

A brain-dump todo app powered by Claude. Dump your thoughts in plain English — Claude organizes them into a categorized, prioritized todo list that persists across sessions.

## Setup

```bash
npm install
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

## Run

```bash
npm run dev
```

Open http://localhost:3000

## How it works

1. Type anything in the brain dump box (or paste a messy list of thoughts)
2. Hit **Parse with Claude** (or Ctrl/Cmd+Enter)
3. Claude extracts actionable items, categorizes them, and assigns priorities
4. Items are saved to a local SQLite database (`todos.db`) — they persist forever
5. Check items off, delete them, or filter by status

## Stack

- **Backend**: Node.js + Express + TypeScript
- **AI**: Claude Opus 4.6 via `@anthropic-ai/sdk`
- **Storage**: SQLite via `better-sqlite3`
- **Frontend**: Vanilla HTML/CSS/JS (no build step)

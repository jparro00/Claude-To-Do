import 'dotenv/config';
import express, { Request, Response } from 'express';
import path from 'path';
import { getAllTodos, insertTodos, toggleTodo, deleteTodo, clearCompleted } from './database';
import { parseBrainDump } from './claude';

const app = express();
const PORT = process.env.PORT ? parseInt(process.env.PORT) : 3000;

app.use(express.json());
app.use(express.static(path.join(__dirname, '..', 'public')));

// GET all todos
app.get('/api/todos', (_req: Request, res: Response) => {
  try {
    const todos = getAllTodos();
    res.json({ success: true, todos });
  } catch (err) {
    res.status(500).json({ success: false, error: 'Failed to fetch todos' });
  }
});

// POST brain dump → parse with Claude → save todos
app.post('/api/brain-dump', async (req: Request, res: Response) => {
  const { text } = req.body as { text: string };

  if (!text || text.trim().length === 0) {
    res.status(400).json({ success: false, error: 'Brain dump text is required' });
    return;
  }

  try {
    const parsed = await parseBrainDump(text.trim());

    if (parsed.length === 0) {
      res.json({ success: true, added: [], message: 'No actionable items found in your brain dump' });
      return;
    }

    const added = insertTodos(
      parsed.map((item) => ({ ...item, completed: false }))
    );
    res.json({ success: true, added, message: `Added ${added.length} item${added.length !== 1 ? 's' : ''}` });
  } catch (err) {
    const message = err instanceof Error ? err.message : 'Unknown error';
    res.status(500).json({ success: false, error: `Failed to parse brain dump: ${message}` });
  }
});

// PATCH toggle todo completion
app.patch('/api/todos/:id/toggle', (req: Request, res: Response) => {
  const id = parseInt(req.params.id);
  if (isNaN(id)) {
    res.status(400).json({ success: false, error: 'Invalid id' });
    return;
  }
  const todo = toggleTodo(id);
  if (!todo) {
    res.status(404).json({ success: false, error: 'Todo not found' });
    return;
  }
  res.json({ success: true, todo });
});

// DELETE a todo
app.delete('/api/todos/:id', (req: Request, res: Response) => {
  const id = parseInt(req.params.id);
  if (isNaN(id)) {
    res.status(400).json({ success: false, error: 'Invalid id' });
    return;
  }
  const deleted = deleteTodo(id);
  if (!deleted) {
    res.status(404).json({ success: false, error: 'Todo not found' });
    return;
  }
  res.json({ success: true });
});

// DELETE completed todos
app.delete('/api/todos/completed/clear', (_req: Request, res: Response) => {
  const count = clearCompleted();
  res.json({ success: true, cleared: count });
});

app.listen(PORT, () => {
  console.log(`\n🚀 Todo app running at http://localhost:${PORT}\n`);
  if (!process.env.ANTHROPIC_API_KEY) {
    console.warn('⚠️  ANTHROPIC_API_KEY not set — brain dump parsing will fail\n');
  }
});

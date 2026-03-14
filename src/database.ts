import Database from 'better-sqlite3';
import path from 'path';

const DB_PATH = path.join(process.cwd(), 'todos.db');

const db = new Database(DB_PATH);

db.exec(`
  CREATE TABLE IF NOT EXISTS todos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text TEXT NOT NULL,
    category TEXT DEFAULT 'General',
    priority TEXT DEFAULT 'medium',
    completed INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now')),
    completed_at TEXT
  )
`);

export interface Todo {
  id: number;
  text: string;
  category: string;
  priority: 'low' | 'medium' | 'high';
  completed: boolean;
  created_at: string;
  completed_at: string | null;
}

interface DbRow {
  id: number;
  text: string;
  category: string;
  priority: string;
  completed: number;
  created_at: string;
  completed_at: string | null;
}

function rowToTodo(row: DbRow): Todo {
  return {
    ...row,
    priority: row.priority as Todo['priority'],
    completed: row.completed === 1,
  };
}

export function getAllTodos(): Todo[] {
  const rows = db.prepare('SELECT * FROM todos ORDER BY completed ASC, created_at DESC').all() as DbRow[];
  return rows.map(rowToTodo);
}

export function insertTodos(items: Omit<Todo, 'id' | 'created_at' | 'completed_at'>[]): Todo[] {
  const insert = db.prepare(
    'INSERT INTO todos (text, category, priority, completed) VALUES (@text, @category, @priority, 0)'
  );
  const inserted: Todo[] = [];
  const insertMany = db.transaction(() => {
    for (const item of items) {
      const info = insert.run({ text: item.text, category: item.category, priority: item.priority });
      const row = db.prepare('SELECT * FROM todos WHERE id = ?').get(info.lastInsertRowid) as DbRow;
      inserted.push(rowToTodo(row));
    }
  });
  insertMany();
  return inserted;
}

export function toggleTodo(id: number): Todo | null {
  const todo = db.prepare('SELECT * FROM todos WHERE id = ?').get(id) as DbRow | undefined;
  if (!todo) return null;
  const newCompleted = todo.completed === 1 ? 0 : 1;
  const completedAt = newCompleted === 1 ? new Date().toISOString() : null;
  db.prepare('UPDATE todos SET completed = ?, completed_at = ? WHERE id = ?').run(newCompleted, completedAt, id);
  return rowToTodo(db.prepare('SELECT * FROM todos WHERE id = ?').get(id) as DbRow);
}

export function deleteTodo(id: number): boolean {
  const result = db.prepare('DELETE FROM todos WHERE id = ?').run(id);
  return result.changes > 0;
}

export function clearCompleted(): number {
  const result = db.prepare('DELETE FROM todos WHERE completed = 1').run();
  return result.changes;
}

export default db;

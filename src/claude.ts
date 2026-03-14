import Anthropic from '@anthropic-ai/sdk';

const client = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY,
});

export interface ParsedTodoItem {
  text: string;
  category: string;
  priority: 'low' | 'medium' | 'high';
}

const SYSTEM_PROMPT = `You are a personal productivity assistant that transforms brain dumps into organized todo lists.

When given a brain dump of tasks, thoughts, or things to do, extract each actionable item and return them as structured JSON.

For each item:
- "text": Clear, concise action item (start with a verb when possible)
- "category": Group into one of: Work, Personal, Shopping, Health, Finance, Home, Learning, or Other
- "priority": "high" (urgent/important), "medium" (normal), or "low" (nice to have)

Rules:
- Only include actionable items (skip vague thoughts or non-tasks)
- Keep text short and clear (under 100 characters)
- Infer priority from urgency words like "urgent", "ASAP", "by Friday", etc.
- Return ONLY valid JSON array, no extra text

Example output:
[
  {"text": "Call dentist to schedule appointment", "category": "Health", "priority": "medium"},
  {"text": "Buy groceries: milk, eggs, bread", "category": "Shopping", "priority": "high"}
]`;

export async function parseBrainDump(text: string): Promise<ParsedTodoItem[]> {
  const stream = await client.messages.stream({
    model: 'claude-opus-4-6',
    max_tokens: 2048,
    system: SYSTEM_PROMPT,
    messages: [
      {
        role: 'user',
        content: `Parse this brain dump into todo items:\n\n${text}`,
      },
    ],
  });

  const message = await stream.finalMessage();

  const responseText = message.content
    .filter((b) => b.type === 'text')
    .map((b) => (b as { type: 'text'; text: string }).text)
    .join('');

  // Extract JSON from the response
  const jsonMatch = responseText.match(/\[[\s\S]*\]/);
  if (!jsonMatch) {
    throw new Error('Claude did not return a valid JSON array');
  }

  const parsed = JSON.parse(jsonMatch[0]) as ParsedTodoItem[];

  // Validate and normalize
  return parsed.map((item) => ({
    text: String(item.text).slice(0, 200),
    category: String(item.category || 'Other'),
    priority: (['low', 'medium', 'high'].includes(item.priority) ? item.priority : 'medium') as ParsedTodoItem['priority'],
  }));
}

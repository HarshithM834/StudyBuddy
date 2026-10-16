export type Lecture = { id: string; name: string; course: string; page_count: number; example: string | null };
export type Slide = { number: number; title: string; width: number; height: number; has_text: boolean; has_work: boolean };
export type Deck = Lecture & { pages: Slide[] };
export type Mark = { id: string; kind: 'highlight' | 'pin'; x: number; y: number; width: number; height: number; text: string };
export type Visual = { title: string; nodes: { id: string; label: string }[]; edges: { source: string; target: string; label: string }[] };
export type Message = { id: string; role: 'user' | 'assistant'; content: string; citations: number[]; visual: Visual | null };
export type Work = { notes: string; marks: Mark[]; messages: Message[] };
export type Health = { status: string; tutor_configured: boolean; provider: 'local'; model: string; ocr_available: boolean };
export type Intent = 'ask' | 'explain' | 'visualize' | 'quiz';

export async function api<T>(path: string, init: RequestInit = {}): Promise<T> {
  const response = await fetch('/api' + path, init);
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(typeof body.detail === 'string' ? body.detail : `The request couldn't be completed (${response.status}).`);
  }
  return response.json();
}
export function json(method: string, body: unknown): RequestInit {
  return { method, headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) };
}

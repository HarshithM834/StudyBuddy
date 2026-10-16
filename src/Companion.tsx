import { useEffect, useRef, useState } from 'react';
import { BookOpen, Pause, Play, Plus, ArrowUp, X, Lightbulb, Sparkles, CircleHelp } from 'lucide-react';
import ReactMarkdown, { type Components } from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { api, json, type Lecture, type Message, type Work, type Intent } from './types';
import { ConceptDiagram } from './VisualLab';
import './companion.css';

// Generated Markdown cannot fetch external images or navigate the native view.
const localMarkdown: Components = { img: () => null, a: ({ children }) => <span>{children}</span> };

type Frame = { type: 'frame'; application: string; title: string; text: string; image: string; capturedAt: number };
type NativeEvent = Frame | { type: 'status'; active: boolean; message: string } | { type: 'changing'; message: string };
type View = { key: string; label: string; frame: Frame; document?: string; page?: number };
type NativeWindow = Window & { webkit?: { messageHandlers?: { studybuddy?: { postMessage: (value: { action: string }) => void } } } };
function native(action: string) { (window as NativeWindow).webkit?.messageHandlers?.studybuddy?.postMessage({ action }); }
async function contextKey(frame: Frame) {
  // Recognized PDFs use document/page identity. For other apps this is an exact
  // normalized visible-text identity, not a claim of durable URL/video tracking.
  const value = `${frame.application}\n${frame.title}\n${frame.text.toLowerCase().replace(/\s+/g, ' ').trim()}${frame.text.trim().split(/\s+/).length < 6 ? '\n' + frame.image : ''}`;
  const hash = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(value));
  return Array.from(new Uint8Array(hash)).map(byte => byte.toString(16).padStart(2, '0')).join('');
}

export default function Companion() {
  const isNative = Boolean((window as NativeWindow).webkit?.messageHandlers?.studybuddy);
  const [active, setActive] = useState(false);
  const [status, setStatus] = useState('Study mode is paused');
  const [view, setView] = useState<View | null>(null);
  const [lectures, setLectures] = useState<Lecture[]>([]);
  const [course, setCourse] = useState('');
  const [prepared, setPrepared] = useState(false);
  const [preparing, setPreparing] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [notes, setNotes] = useState('');
  const [loading, setLoading] = useState(false);
  const [loadedKey, setLoadedKey] = useState('');
  const [source, setSource] = useState<{ document: string; page: number } | null>(null);
  const [drafts, setDrafts] = useState<Record<string, string>>({});
  const [pending, setPending] = useState<{ key: string; label: string; message: string } | null>(null);
  const [autoExplain, setAutoExplain] = useState(false);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  const [showNotes, setShowNotes] = useState(false);
  const uploader = useRef<HTMLInputElement>(null);
  const currentView = useRef<View | null>(null);
  const requestBusy = useRef(false);
  const frameSequence = useRef(0);
  const following = useRef(false);
  const courseRef = useRef({ id: '', ready: false });
  const stable = useRef({ key: '', count: 0 });
  const autoAttempted = useRef(new Set<string>());
  const key = view?.key || '';
  const question = drafts[key] || '';
  const workPath = view?.document && view.page ? `/documents/${view.document}/pages/${view.page}` : null;
  const readyToAsk = active && Boolean(view) && !loading && loadedKey === key && !pending;

  function changeView(next: View | null) { currentView.current = next; setView(next); }
  function pause() {
    following.current = false; frameSequence.current++; stable.current = { key: '', count: 0 };
    setActive(false); setStatus('Paused · screen capture stopped'); setAutoExplain(false); changeView(null);
    native('pause');
  }

  useEffect(() => {
    api<Lecture[]>('/documents').then(setLectures).catch(reason => setError(reason.message));
    const onNative = (event: Event) => {
      const value = (event as CustomEvent<NativeEvent>).detail;
      if (value.type === 'status') {
        following.current = value.active; setActive(value.active); setStatus(value.message);
        if (!value.active) { frameSequence.current++; changeView(null); setAutoExplain(false); stable.current = { key: '', count: 0 }; }
        return;
      }
      if (value.type === 'changing') { frameSequence.current++; changeView(null); stable.current = { key: '', count: 0 }; setStatus(value.message); return; }
      if (!following.current) return;
      const sequence = ++frameSequence.current;
      const selected = courseRef.current;
      void (async () => {
        const screenKey = await contextKey(value);
        let next: View = { key: screenKey, label: value.title || value.application, frame: value };
        let state = `Following ${value.application} · visible content`;
        if (selected.id && selected.ready) {
          try {
            const match = await api<{ page: number | null; status: string }>(`/documents/${selected.id}/follow/match`, json('POST', { text: value.text }));
            if (sequence !== frameSequence.current || !following.current) return;
            if (match.page) {
              const candidate = `${selected.id}:${match.page}`;
              stable.current = { key: candidate, count: stable.current.key === candidate ? stable.current.count + 1 : 1 };
              if (stable.current.count >= 2) {
                next = { ...next, key: candidate, label: `PDF slide ${match.page}`, document: selected.id, page: match.page };
                state = `Following ${value.application} · slide ${match.page}`;
              } else { state = `Following ${value.application} · checking slide…`; }
            } else {
              stable.current = { key: '', count: 0 };
              state = match.status === 'ambiguous' ? 'Multiple slides may be visible · using screen context' : `Following ${value.application} · no confident PDF match`;
            }
          } catch { state = `Following ${value.application} · PDF matching unavailable`; stable.current = { key: '', count: 0 }; }
        }
        if (sequence !== frameSequence.current || !following.current) return;
        setStatus(state); changeView(next);
      })().catch(() => { if (sequence === frameSequence.current) { changeView(null); setError('Could not read this view. Pause and resume study mode.'); } });
    };
    window.addEventListener('studybuddy:screen', onNative);
    native('ready');
    return () => { window.removeEventListener('studybuddy:screen', onNative); following.current = false; frameSequence.current++; native('pause'); };
  }, []);

  useEffect(() => {
    courseRef.current = { id: course, ready: false }; setPrepared(false);
    stable.current = { key: '', count: 0 }; frameSequence.current++;
    changeView(null);
    if (!course) { setPreparing(false); return; }
    let valid = true; setPreparing(true);
    api(`/documents/${course}/follow/prepare`, json('POST', {})).then(() => {
      if (valid) { courseRef.current = { id: course, ready: true }; setPrepared(true); }
    }).catch(reason => valid && setError(reason.message)).finally(() => valid && setPreparing(false));
    return () => { valid = false; };
  }, [course]);

  useEffect(() => {
    setMessages([]); setNotes(''); setShowNotes(false); setError(''); setLoadedKey(''); setSource(null);
    if (!view) { setLoading(false); return; }
    const controller = new AbortController(); setLoading(true);
    const path = view.document ? `/documents/${view.document}/pages/${view.page}/work` : `/companion/contexts/${view.key}`;
    api<{ messages: Message[]; notes?: string }>(path, { signal: controller.signal }).then(result => {
      if (controller.signal.aborted) return;
      setMessages(result.messages); setNotes(result.notes || ''); setLoadedKey(key);
    }).catch(reason => { if (!controller.signal.aborted) setError(reason.message); }).finally(() => { if (!controller.signal.aborted) setLoading(false); });
    return () => controller.abort();
  }, [key]);

  async function send(message: string, intent: Intent = 'ask') {
    const origin = currentView.current;
    if (!origin || !following.current || requestBusy.current || loading || !message.trim()) return;
    requestBusy.current = true;
    setPending({ key: origin.key, label: origin.label, message }); setError('');
    try {
      const result = origin.document
        ? await api<{ messages: Message[] }>(`/documents/${origin.document}/pages/${origin.page}/chat`, json('POST', { message, intent }))
        : await api<{ messages: Message[] }>('/companion/chat', json('POST', { message, intent, context_id: origin.key, application: origin.frame.application, title: origin.frame.title, text: origin.frame.text, image: origin.frame.image }));
      // A late answer belongs to the captured view, never the newer screen.
      if (currentView.current?.key === origin.key) setMessages(result.messages);
      else setNotice(`Answer saved for ${origin.label}. Return to that view to read it.`);
      setDrafts(old => old[origin.key] === message ? { ...old, [origin.key]: '' } : old);
    } catch (reason) {
      setDrafts(old => ({ ...old, [origin.key]: old[origin.key] || message }));
      setError(`${origin.label}: ${(reason as Error).message}`);
    } finally { requestBusy.current = false; setPending(null); }
  }

  useEffect(() => {
    if (!autoExplain || !active || !view?.document || loading || loadedKey !== key || pending || messages.length || autoAttempted.current.has(key)) return;
    // Two native frames establish the slide; a further quiet interval avoids
    // generating while a student is quickly paging. There is no work queue.
    const timer = setTimeout(() => {
      if (!following.current || currentView.current?.key !== key || requestBusy.current) return;
      autoAttempted.current.add(key);
      void send('Explain the main idea of this slide briefly, using the course notation.', 'explain');
    }, 1800);
    return () => clearTimeout(timer);
  }, [autoExplain, active, key, loading, loadedKey, pending, messages.length]);

  async function upload(file?: File) {
    if (!file) return;
    if (file.size > 32 * 1024 * 1024) { setError('Choose a PDF smaller than 32 MB.'); return; }
    setUploading(true); setError('');
    try {
      const form = new FormData(); form.append('file', file);
      const lecture = await api<Lecture>('/documents', { method: 'POST', body: form });
      setLectures(await api<Lecture[]>('/documents')); setCourse(lecture.id);
    } catch (reason) { setError((reason as Error).message); }
    finally { setUploading(false); if (uploader.current) uploader.current.value = ''; }
  }

  async function saveAnswer(message: Message) {
    const path = workPath, originalKey = key;
    if (!path) return;
    try {
      const saved = await api<Work>(path + '/work');
      const text = [saved.notes, message.content].filter(Boolean).join('\n\n');
      await api(path + '/notes', json('PUT', { text }));
      if (currentView.current?.key === originalKey) { setNotes(text); setShowNotes(true); }
      setNotice('Saved to this slide’s notes.');
    } catch (reason) { setError((reason as Error).message); }
  }

  return <main className="companion-shell">
    <header className="companion-header"><span className="companion-brand"><BookOpen size={19} />StudyBuddy</span><span className="alpha-tag">ALPHA</span><button aria-label="Hide companion and pause" onClick={() => { pause(); native('hide'); }}><X size={18} /></button></header>
    <section className={`follow-status ${active ? 'is-active' : ''}`} aria-live="polite"><span className="follow-dot" /><span>{status}</span><button disabled={!isNative} onClick={() => active ? pause() : native('start')} aria-label={active ? 'Pause study mode' : 'Start study mode'}>{active ? <Pause size={16} /> : <Play size={16} />}</button></section>
    {!isNative && <p className="companion-warning">Screen following is available in the Mac menu-bar app. This browser view is for development.</p>}
    <details className="course-context"><summary>Course material <span>{course ? 'PDF attached' : 'Optional'}</span></summary><p>Add lecture slides for course context and saved explanations by slide. Study mode still follows other apps.</p><div><select aria-label="Course PDF context" value={course} onChange={event => { setCourse(event.target.value); setAutoExplain(false); }}><option value="">Visible screen only</option>{lectures.map(item => <option value={item.id} key={item.id}>{item.name}</option>)}</select><button disabled={uploading} onClick={() => uploader.current?.click()} aria-label="Add course PDF"><Plus size={19} /></button></div><input type="file" ref={uploader} accept="application/pdf,.pdf" hidden onChange={event => void upload(event.target.files?.[0])} />{uploading && <p>Adding lecture…</p>}{preparing && <p>Reading lecture slides locally… You can still ask about the visible screen.</p>}{prepared && <label className="auto-explain"><input type="checkbox" checked={autoExplain} onChange={event => setAutoExplain(event.target.checked)} />Explain as I go · recognized PDF slides</label>}</details>
    {error && <div className="companion-warning" role="alert">{error}<button aria-label="Dismiss error" onClick={() => setError('')}>×</button></div>}
    {notice && <div className="companion-notice" role="status">{notice}<button aria-label="Dismiss notice" onClick={() => setNotice('')}>×</button></div>}
    <div className="companion-content">
      {!view ? <section className="companion-welcome"><span className="empty-emblem"><BookOpen size={28} /></span><h1>Right here, as you study.</h1><p>Open Canvas, a video, or your lecture slides. Turn on study mode and I’ll follow your active window.</p><p className="companion-small">You control when screen reading starts. Hiding this panel pauses it. Audio and off-screen content aren’t included.</p>{!active && <button className="primary-button" disabled={!isNative} onClick={() => native('start')}><Play size={15} />Turn on study mode</button>}</section> : <>
        <section className="current-context"><div><span>{view.frame.application}</span><strong>{view.label}</strong><small>{view.document ? 'Matched to your course PDF' : 'Visible screen · no audio or off-screen material'}</small></div><img src={view.frame.image} alt="Current study window snapshot" /></section>
        {loading || loadedKey !== key ? <p className="companion-small">Restoring this view’s saved work…</p> : <>
          {!messages.length && <p className="companion-intro">What would help with this part?</p>}
          <div className="companion-actions"><button disabled={!readyToAsk} onClick={() => void send('Explain what is visible here. Start with the main idea and acknowledge missing context.', 'explain')}><Lightbulb size={15} />Explain</button><button disabled={!readyToAsk} onClick={() => void send('Show the key idea visually, using only what you can establish here.', 'visualize')}><Sparkles size={15} />Visualize</button><button disabled={!readyToAsk} onClick={() => void send('Ask one application question about this material and wait for my answer.', 'quiz')}><CircleHelp size={15} />Quiz me</button></div>
          {view.document && <button className="saved-notes-toggle" onClick={() => setShowNotes(!showNotes)}>{showNotes ? 'Hide' : 'Show'} saved slide notes</button>}
          {showNotes && <section className="companion-notes"><ReactMarkdown remarkPlugins={[remarkGfm]} components={localMarkdown}>{notes || 'No notes saved on this slide yet.'}</ReactMarkdown></section>}
          {source && <section className="source-preview"><button onClick={() => setSource(null)}>Close source · PDF page {source.page}</button><img src={`/api/documents/${source.document}/pages/${source.page}/image?width=1000`} alt={`Source PDF page ${source.page}`} /></section>}
          <div aria-label="Conversation for current view">{messages.map(message => <article className={`message ${message.role}`} key={message.id}><div className="message-author">{message.role === 'user' ? 'You' : 'StudyBuddy'}</div><ReactMarkdown remarkPlugins={[remarkGfm]} components={localMarkdown}>{message.content}</ReactMarkdown>{message.visual && <ConceptDiagram visual={message.visual} />}{message.citations.length > 0 && <div className="companion-sources">PDF sources: {message.citations.map(page => <button key={page} onClick={() => view.document && setSource({ document: view.document, page })}>Page {page}</button>)}</div>}{message.role === 'assistant' && workPath && <button className="save-answer" onClick={() => void saveAnswer(message)}>Save to slide notes</button>}</article>)}</div>
        </>}
      </>}
    </div>
    {pending && <div className="companion-pending" role="status">Thinking about {pending.label}…{pending.key !== key && ' You can keep moving; the answer stays with that view.'}</div>}
    <form className="companion-composer" onSubmit={event => { event.preventDefault(); void send(question); }}><textarea aria-label="Ask about what you are viewing" placeholder={active ? 'Ask about what you’re viewing…' : 'Turn on study mode to ask…'} value={question} disabled={!view} onChange={event => setDrafts(old => ({ ...old, [key]: event.target.value }))} /><button aria-label="Send question" disabled={!readyToAsk || !question.trim()}><ArrowUp size={19} /></button></form>
    <footer className="companion-footer">On this Mac · local AI · answers may be wrong</footer>
  </main>;
}

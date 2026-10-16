import { useCallback, useEffect, useRef, useState, type PointerEvent } from 'react';
import { ArrowDownToLine, ArrowLeft, ArrowRight, ArrowUp, BookOpen, Check, ChevronDown, ChevronLeft, ChevronRight, CircleHelp, FileText, Highlighter, Lightbulb, LoaderCircle, Maximize2, Menu, MessageCircle, MousePointer2, PanelLeftClose, PencilLine, Pin, Plus, Search, Sparkles, StickyNote, Trash2, Undo2, Upload, X } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { api, json, type Deck, type Health, type Intent, type Lecture, type Mark, type Message, type Work } from './types';
import VisualLab, { ConceptDiagram } from './VisualLab';

const emptyWork: Work = { notes: '', marks: [], messages: [] };
const prompts: { label: string; intent: Intent; message: string; icon: typeof Lightbulb }[] = [
  { label: 'Explain this slide', intent: 'explain', message: 'Help me understand this slide. Start with the main idea and use the notation shown here.', icon: Lightbulb },
  { label: 'Show me visually', intent: 'visualize', message: 'Make a simple visual explanation of the key idea on this slide.', icon: Sparkles },
  { label: 'Check my understanding', intent: 'quiz', message: 'Ask me one application question about this slide, then wait for my answer.', icon: CircleHelp },
];

function initialLocation() {
  try { return JSON.parse(localStorage.getItem('studybuddy:last-place') || 'null') as { document: string; page: number } | null; }
  catch { return null; }
}

export default function App() {
  const [lectures, setLectures] = useState<Lecture[]>([]);
  const [documentId, setDocumentId] = useState('');
  const [deck, setDeck] = useState<Deck | null>(null);
  const [page, setPage] = useState(1);
  const [health, setHealth] = useState<Health | null>(null);
  const [work, setWork] = useState<Work>(emptyWork);
  const [loading, setLoading] = useState(true);
  const [workLoading, setWorkLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [chatting, setChatting] = useState(false);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  const [sidebar, setSidebar] = useState(() => window.innerWidth >= 1000);
  const [focusView, setFocusView] = useState(false);
  const [search, setSearch] = useState('');
  const [panel, setPanel] = useState<'tutor' | 'notes'>('tutor');
  const [tool, setTool] = useState<'read' | 'highlight' | 'pin'>('read');
  const [draftMark, setDraftMark] = useState<Mark | null>(null);
  const [notesStatus, setNotesStatus] = useState<'saved' | 'saving' | 'unsaved' | 'error'>('saved');
  const [question, setQuestion] = useState('');
  const [pendingQuestion, setPendingQuestion] = useState('');
  const [lab, setLab] = useState(false);
  const [connectionModal, setConnectionModal] = useState(false);
  const [imageReady, setImageReady] = useState(false);
  const [imageError, setImageError] = useState(false);
  const [markSaving, setMarkSaving] = useState(false);
  const [navigating, setNavigating] = useState(false);
  const uploader = useRef<HTMLInputElement>(null);
  const frame = useRef<HTMLDivElement>(null);
  const chatEnd = useRef<HTMLDivElement>(null);
  const connectionDialog = useRef<HTMLElement>(null);
  const noteTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const pendingNote = useRef<{ path: string; text: string } | null>(null);
  const noteQueue = useRef<Promise<void>>(Promise.resolve());
  const currentWorkKey = useRef('');
  const location = initialLocation();
  const slide = deck?.pages.find(slide => slide.number === page);
  const workPath = `/documents/${documentId}/pages/${page}`;
  const canLab = deck?.example === 'cyse425-week6' && page >= 21 && page <= 23;
  const busy = chatting || markSaving || navigating || workLoading;

  useEffect(() => {
    let active = true;
    Promise.all([api<Lecture[]>('/documents'), api<Health>('/health')]).then(([list, status]) => {
      if (!active) return;
      setLectures(list); setHealth(status);
      const selected = list.find(item => item.id === location?.document) || list[0];
      if (selected) {
        setDocumentId(selected.id);
        setPage(location?.document === selected.id ? Math.max(1, Math.min(location.page, selected.page_count)) : 1);
      }
    }).catch(reason => active && setError(reason.message)).finally(() => active && setLoading(false));
    return () => { active = false; };
  }, []);

  useEffect(() => {
    if (!documentId) return;
    const controller = new AbortController();
    setDeck(null);
    api<Deck>(`/documents/${documentId}`, { signal: controller.signal }).then(setDeck).catch(reason => { if (reason.name !== 'AbortError') setError(reason.message); });
    return () => controller.abort();
  }, [documentId]);

  useEffect(() => {
    if (!documentId) return;
    const controller = new AbortController();
    currentWorkKey.current = workPath;
    setWorkLoading(true); setWork(emptyWork); setImageReady(false); setImageError(false); setLab(false); setTool('read'); setDraftMark(null); setQuestion(''); setNotesStatus('saved');
    api<Work>(workPath + '/work', { signal: controller.signal }).then(result => {
      setWork(result);
      try { localStorage.setItem('studybuddy:last-place', JSON.stringify({ document: documentId, page })); } catch { /* browser storage is optional */ }
    }).catch(reason => { if (reason.name !== 'AbortError') setError(reason.message); }).finally(() => { if (!controller.signal.aborted) setWorkLoading(false); });
    return () => controller.abort();
  }, [documentId, page]);

  useEffect(() => { chatEnd.current?.scrollIntoView({ behavior: 'smooth', block: 'nearest' }); }, [work.messages, chatting]);
  useEffect(() => { if (!notice) return; const timer = setTimeout(() => setNotice(''), 3500); return () => clearTimeout(timer); }, [notice]);

  useEffect(() => {
    if (!connectionModal) return;
    const previousFocus = document.activeElement as HTMLElement | null;
    const dialog = connectionDialog.current;
    const controls = () => Array.from(dialog?.querySelectorAll<HTMLElement>('button:not([disabled]), a[href], input, textarea, [tabindex="0"]') || []);
    controls()[0]?.focus();
    const onKey = (event: KeyboardEvent) => {
      if (event.key === 'Escape') { event.preventDefault(); setConnectionModal(false); }
      if (event.key !== 'Tab') return;
      const items = controls();
      const first = items[0], last = items[items.length - 1];
      if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last?.focus(); }
      else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first?.focus(); }
    };
    dialog?.addEventListener('keydown', onKey);
    return () => { dialog?.removeEventListener('keydown', onKey); previousFocus?.focus(); };
  }, [connectionModal]);

  const flushNotes = useCallback(async () => {
    if (noteTimer.current) { clearTimeout(noteTimer.current); noteTimer.current = null; }
    const pending = pendingNote.current;
    if (!pending) { await noteQueue.current; return; }
    pendingNote.current = null;
    setNotesStatus('saving');
    const operation = noteQueue.current.catch(() => undefined).then(async () => {
      await api(pending.path + '/notes', json('PUT', { text: pending.text }));
      if (currentWorkKey.current === pending.path && !pendingNote.current) setNotesStatus('saved');
    });
    noteQueue.current = operation;
    try { await operation; }
    catch (reason) {
      if (!pendingNote.current) pendingNote.current = pending;
      setNotesStatus('error');
      throw reason;
    }
  }, []);

  function updateNotes(text: string) {
    setWork(value => ({ ...value, notes: text })); setNotesStatus('unsaved');
    pendingNote.current = { path: workPath, text };
    if (noteTimer.current) clearTimeout(noteTimer.current);
    noteTimer.current = setTimeout(() => { void flushNotes().catch(reason => setError(reason.message)); }, 650);
  }

  useEffect(() => {
    const protect = (event: BeforeUnloadEvent) => { if (pendingNote.current || notesStatus === 'saving') event.preventDefault(); };
    window.addEventListener('beforeunload', protect);
    return () => window.removeEventListener('beforeunload', protect);
  }, [notesStatus]);

  async function navigate(target: number, nextDocument = documentId) {
    if (busy || (target === page && nextDocument === documentId)) return;
    setNavigating(true);
    try {
      await flushNotes(); setDocumentId(nextDocument); setPage(target); setError('');
      if (window.innerWidth < 1000) setSidebar(false);
    } catch (reason) { setError((reason as Error).message); }
    finally { setNavigating(false); }
  }

  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      const tag = (event.target as HTMLElement).tagName;
      if (['INPUT', 'TEXTAREA', 'SELECT', 'BUTTON'].includes(tag) || (event.target as HTMLElement).isContentEditable || connectionModal) return;
      if (event.key === 'ArrowRight' && deck && page < deck.page_count) { event.preventDefault(); void navigate(page + 1); }
      if (event.key === 'ArrowLeft' && page > 1) { event.preventDefault(); void navigate(page - 1); }
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  });

  async function upload(file: File | undefined) {
    if (!file) return;
    if (file.size > 32 * 1024 * 1024) { setError('Choose a PDF smaller than 32 MB.'); return; }
    setUploading(true); setError('');
    try {
      await flushNotes();
      const form = new FormData(); form.append('file', file);
      const document = await api<Lecture>('/documents', { method: 'POST', body: form });
      const list = await api<Lecture[]>('/documents'); setLectures(list);
      setDocumentId(document.id); setPage(1); setNotice('Lecture added to your library.');
    } catch (reason) { setError((reason as Error).message); }
    finally { setUploading(false); if (uploader.current) uploader.current.value = ''; }
  }

  async function persistMarks(marks: Mark[]) {
    if (markSaving) return;
    setMarkSaving(true);
    try { await api(workPath + '/marks', json('PUT', { marks })); setWork(value => ({ ...value, marks })); }
    catch (reason) { setError((reason as Error).message); }
    finally { setMarkSaving(false); }
  }

  function point(event: PointerEvent) {
    const rect = frame.current!.getBoundingClientRect();
    return { x: Math.max(0, Math.min(1, (event.clientX - rect.left) / rect.width)), y: Math.max(0, Math.min(1, (event.clientY - rect.top) / rect.height)) };
  }

  function startMark(event: PointerEvent<HTMLDivElement>) {
    if (tool === 'read' || busy || !imageReady || event.button !== 0) return;
    event.preventDefault();
    const { x, y } = point(event);
    if (tool === 'pin') {
      void persistMarks([...work.marks, { id: crypto.randomUUID(), kind: 'pin', x, y, width: 0, height: 0, text: '' }]);
      setPanel('notes'); setTool('read'); return;
    }
    event.currentTarget.setPointerCapture(event.pointerId);
    setDraftMark({ id: crypto.randomUUID(), kind: 'highlight', x, y, width: 0, height: 0, text: '' });
  }

  function moveMark(event: PointerEvent<HTMLDivElement>) {
    if (!draftMark) return;
    const pos = point(event);
    setDraftMark(mark => mark && ({ ...mark, width: pos.x - mark.x, height: pos.y - mark.y }));
  }

  function endMark() {
    if (!draftMark) return;
    const normalized = { ...draftMark, x: Math.min(draftMark.x, draftMark.x + draftMark.width), y: Math.min(draftMark.y, draftMark.y + draftMark.height), width: Math.abs(draftMark.width), height: Math.abs(draftMark.height) };
    setDraftMark(null);
    if (normalized.width > .008 && normalized.height > .008) void persistMarks([...work.marks, normalized]);
  }

  async function send(message = question, intent: Intent = 'ask') {
    if (!message.trim() || chatting || workLoading) return;
    if (!health?.tutor_configured) { setConnectionModal(true); return; }
    setChatting(true); setPendingQuestion(message); setQuestion(''); setError(''); setPanel('tutor');
    try {
      const result = await api<{ messages: Message[] }>(workPath + '/chat', json('POST', { message, intent }));
      setWork(value => ({ ...value, messages: result.messages }));
    } catch (reason) { setError((reason as Error).message); setQuestion(message); }
    finally { setChatting(false); setPendingQuestion(''); }
  }

  async function saveAnswer(message: Message) {
    updateNotes([work.notes, message.content].filter(Boolean).join('\n\n'));
    setPanel('notes');
    try { await flushNotes(); setNotice('Explanation saved to this slide’s notes.'); }
    catch (reason) { setError((reason as Error).message); }
  }

  function exportNotes() {
    const content = `# ${deck?.name} — PDF slide ${page}\n\n${work.notes}\n\n${work.marks.filter(mark => mark.kind === 'pin' && mark.text).map((mark, i) => `Pin ${i + 1}: ${mark.text}`).join('\n\n')}`;
    const url = URL.createObjectURL(new Blob([content], { type: 'text/markdown;charset=utf-8' }));
    const link = document.createElement('a'); link.href = url; link.download = `studybuddy-slide-${page}.md`; link.click(); URL.revokeObjectURL(url);
  }

  async function refreshConnection() {
    try {
      const result = await api<Health>('/health'); setHealth(result);
      setNotice(result.tutor_configured ? 'Tutor connection detected. You can ask a question.' : 'The local tutor isn’t running yet. Slides and notes are ready.');
      if (result.tutor_configured) setConnectionModal(false);
    } catch (reason) { setError((reason as Error).message); }
  }

  return <div className={`app-shell ${sidebar ? '' : 'sidebar-closed'}`}>
    <input ref={uploader} type="file" accept="application/pdf,.pdf" hidden onChange={event => void upload(event.target.files?.[0])} />
    {sidebar && <aside className="sidebar">
      <a href="#" className="brand" onClick={event => event.preventDefault()}><span className="brand-icon"><BookOpen size={21} /></span>studybuddy<span className="brand-dot">.</span></a>
      <button className="upload-button" onClick={() => uploader.current?.click()} disabled={uploading || busy}>{uploading ? <LoaderCircle className="spin" size={17} /> : <Plus size={18} />}Add a lecture</button>
      <div className="sidebar-label">YOUR LIBRARY <span>{lectures.length}</span></div>
      <div className="lecture-list">{lectures.map(lecture => <button key={lecture.id} disabled={busy} className={`lecture-item ${lecture.id === documentId ? 'active' : ''}`} onClick={() => void navigate(1, lecture.id)}>
        <span className="lecture-symbol"><FileText size={17} /></span><span><strong>{lecture.name.replace(/\.pdf$/i, '')}</strong><small>{lecture.course} · {lecture.page_count} slides</small></span>{lecture.id === documentId && <ChevronDown size={14} />}
      </button>)}</div>
      {deck && <><div className="slide-list-heading"><span className="sidebar-label">SLIDES</span><button className="icon-button" title="Hide slide navigation" aria-label="Hide slide navigation" onClick={() => setSidebar(false)}><PanelLeftClose size={15} /></button></div>
      <label className="slide-search"><Search size={14} /><input aria-label="Find a slide" placeholder="Find a slide…" value={search} onChange={event => setSearch(event.target.value)} /><span>⌕</span></label>
      <nav className="slide-list" aria-label="Slides">{deck.pages.filter(slide => !search || `${slide.number} ${slide.title}`.toLowerCase().includes(search.toLowerCase())).map(item => <button key={item.number} disabled={busy} aria-current={page === item.number ? 'page' : undefined} aria-label={`Slide ${item.number}: ${item.title}`} className={`slide-item ${page === item.number ? 'selected' : ''}`} onClick={() => void navigate(item.number)}>
        <span className="slide-num">{String(item.number).padStart(2, '0')}</span><span className="slide-mini"><img loading="lazy" src={`/api/documents/${documentId}/pages/${item.number}/image?width=180`} alt="" /></span><span className="slide-title">{item.title}</span>{Boolean(item.has_work) && <span className="work-dot" title="Saved notes or annotations" />}
      </button>)}</nav></>}
      <div className="sidebar-bottom"><span className="avatar">Y</span><div><strong>Your workspace</strong><small>Saved on this machine</small></div><span className="alpha-tag">EARLY</span></div>
    </aside>}

    <main className="workspace">
      <header className="topbar"><div className="breadcrumbs"><button className="icon-button" aria-label="Toggle library" onClick={() => setSidebar(!sidebar)}><Menu size={19} /></button><span>{deck?.course || 'Your library'}</span><ChevronRight size={14} /><strong>{deck ? 'Lecture workspace' : 'Study workspace'}</strong></div><div className="top-actions"><span className="local-badge"><span />Personal workspace</span><button className="icon-button" aria-label="How this workspace works" onClick={() => setConnectionModal(true)}><CircleHelp size={18} /></button></div></header>
      {error && <div className="error-banner" role="alert"><span>{error}</span><button aria-label="Dismiss error" onClick={() => setError('')}><X size={16} /></button></div>}
      {notice && <div className="toast" role="status"><Check size={15} />{notice}</div>}
      {loading ? <div className="full-empty"><LoaderCircle size={25} className="spin" /><h2>Opening your workspace…</h2></div> : !documentId ? <div className="full-empty"><div className="empty-emblem"><BookOpen size={32} /></div><span className="eyebrow">A little clarity, one slide at a time</span><h1>Make room for understanding.</h1><p>Bring your lecture slides. Keep your questions, notes, and ideas together.</p><button className="primary-button" onClick={() => uploader.current?.click()} disabled={uploading}>{uploading ? <LoaderCircle className="spin" size={17} /> : <Upload size={17} />}Upload your first lecture</button><small>PDF · up to 32 MB · stored in your workspace</small></div> : <>
      <div className="document-header"><div><div className="eyebrow">YOUR STUDY SPACE</div><h1>{deck?.name.replace(/\.pdf$/i, '') || 'Opening lecture…'}</h1><p><FileText size={13} />{deck?.page_count || '…'} slides<span>·</span>Your notes follow you as you go.</p></div><a className="outline-button" href={`/api/documents/${documentId}/file`} target="_blank" rel="noreferrer"><ArrowDownToLine size={15} /><span>Original PDF</span></a></div>
      <div className={`study-layout ${focusView ? 'focus-view' : ''}`}>
        <section className="reading-area" aria-label="Lecture viewer">
          <div className="viewer-toolbar"><div className="tool-group">{([{ id: 'read', icon: MousePointer2, label: 'Read' }, { id: 'highlight', icon: Highlighter, label: 'Highlight' }, { id: 'pin', icon: Pin, label: 'Pin a note' }] as const).map(item => <button key={item.id} aria-pressed={tool === item.id} title={item.label} disabled={busy} className={tool === item.id ? 'active' : ''} onClick={() => setTool(item.id)}><item.icon size={16} /><span>{item.label}</span></button>)}<span className="tool-divider" /><button title="Undo last annotation" aria-label="Undo last annotation" disabled={!work.marks.length || busy} onClick={() => void persistMarks(work.marks.slice(0, -1))}><Undo2 size={16} /></button></div><button className="icon-button" aria-label={focusView ? "Return to split view" : "Expand lecture viewer"} title={focusView ? "Return to split view" : "Expand lecture viewer"} onClick={() => setFocusView(!focusView)}><Maximize2 size={16} /></button></div>
          <div className="slide-stage"><div className={`slide-frame tool-${tool}`} ref={frame} style={{ aspectRatio: slide ? `${slide.width}/${slide.height}` : '4/3' }}>
            {!imageReady && !imageError && <div className="image-loading"><LoaderCircle className="spin" size={23} /></div>}
            {imageError && <div className="image-loading">This slide couldn’t load. Try selecting it again.</div>}
            <img key={`${documentId}-${page}`} className="lecture-image" src={`/api/documents/${documentId}/pages/${page}/image?width=1600`} alt={`PDF slide ${page}: ${slide?.title || ''}`} draggable={false} onLoad={() => setImageReady(true)} onError={() => { setImageReady(false); setImageError(true); }} />
            <div className="annotation-layer" onPointerDown={startMark} onPointerMove={moveMark} onPointerUp={endMark} onPointerCancel={() => setDraftMark(null)}>
              {[...work.marks, ...(draftMark ? [draftMark] : [])].map((mark, index) => mark.kind === 'highlight' ? <div key={mark.id} className="highlight-mark" style={{ left: `${Math.min(mark.x, mark.x + mark.width) * 100}%`, top: `${Math.min(mark.y, mark.y + mark.height) * 100}%`, width: `${Math.abs(mark.width) * 100}%`, height: `${Math.abs(mark.height) * 100}%` }} /> : <button key={mark.id} className="pin-mark" aria-label={`Pinned note ${index + 1}: ${mark.text || 'Add a note'}`} title={mark.text || 'Add a note'} style={{ left: `${mark.x * 100}%`, top: `${mark.y * 100}%` }} onPointerDown={event => event.stopPropagation()} onClick={() => setPanel('notes')}>{work.marks.slice(0, index + 1).filter(item => item.kind === 'pin').length}</button>)}
            </div>
          </div></div>
          <div className="slide-caption"><span>{tool === 'highlight' ? 'Drag over the slide to highlight a region.' : tool === 'pin' ? 'Click the slide to attach a note.' : 'Your lecture, with room to make it yours.'}</span><span>{markSaving ? 'Saving…' : work.marks.length ? `${work.marks.length} annotations saved` : 'PDF page numbers'}</span></div>
          <div className="slide-navigation"><button className="outline-button" disabled={page <= 1 || busy} onClick={() => void navigate(page - 1)}><ChevronLeft size={17} /><span>Previous</span></button><div className="page-position"><span>Slide <strong>{page}</strong> of {deck?.page_count || '…'}</span><div className="progress-track"><div style={{ width: `${page / (deck?.page_count || 1) * 100}%` }} /></div></div><button className="outline-button" disabled={!deck || page >= deck.page_count || busy} onClick={() => void navigate(page + 1)}><span>Next</span><ChevronRight size={17} /></button></div>
          {canLab && <button className={`lab-launcher ${lab ? 'open' : ''}`} onClick={() => setLab(!lab)}><span className="lab-symbol"><Sparkles size={19} /></span><span><strong>Make this concept click</strong><small>Explore a Hamming example from your lecture.</small></span>{lab ? <ChevronDown size={18} /> : <ArrowRight size={18} />}</button>}
          {lab && canLab && <VisualLab onClose={() => setLab(false)} />}
          <div className="reading-footnote"><BookOpen size={14} /><span>{canLab ? 'Visual lab uses the same notation as your slides.' : 'Tip: use the arrow keys to move between slides.'}</span></div>
        </section>

        <aside className="study-panel" aria-label="Study tools">
          <div className="panel-tabs"><button className={panel === 'tutor' ? 'active' : ''} onClick={() => setPanel('tutor')}><Sparkles size={16} />Study buddy</button><button className={panel === 'notes' ? 'active' : ''} onClick={() => setPanel('notes')}><StickyNote size={16} />My notes{work.notes && <span className="tab-dot" />}</button></div>
          <div className="panel-context"><span><span className="context-dot" />On slide {page}</span><span>{panel === 'notes' ? 'Saved with this slide' : 'Your lecture is the context'}</span></div>
          {workLoading ? <div className="panel-loading"><LoaderCircle className="spin" size={22} /><span>Opening this slide’s workspace…</span></div> : panel === 'tutor' ? <>
            <div className="conversation">
              {!work.messages.length && <div className="tutor-welcome"><div className="buddy-emblem"><Sparkles size={23} /></div><h2>A little stuck?<br />Let’s work through it.</h2><p>Ask about this slide, explore an idea visually, or check what you understand.</p><div className="suggestions">{prompts.map(prompt => <button key={prompt.intent} disabled={chatting} onClick={() => void send(prompt.message, prompt.intent)}><prompt.icon size={17} /><span>{prompt.label}</span><ArrowUp size={14} /></button>)}</div>{!health?.tutor_configured && <div className="connection-card"><span className="connection-indicator" /><div><strong>Local tutor is offline</strong><p>Your slides, notes{canLab ? ', and visual lab' : ''} are ready to use.</p><button onClick={() => setConnectionModal(true)}>Start your free local tutor <ArrowRight size={12} /></button></div></div>}</div>}
              {work.messages.map(message => <div className={`message ${message.role}`} key={message.id}><div className="message-author">{message.role === 'assistant' ? <><Sparkles size={13} />Study buddy</> : 'You'}</div><div className="markdown"><ReactMarkdown remarkPlugins={[remarkGfm]}>{message.content}</ReactMarkdown></div>{message.visual && <ConceptDiagram visual={message.visual} />}{message.citations.length > 0 && <div className="citations">{message.citations.map(number => <button key={number} disabled={busy} onClick={() => void navigate(number)}><FileText size={11} />Slide {number}</button>)}</div>}{message.role === 'assistant' && <button className="save-answer" onClick={() => void saveAnswer(message)}><Plus size={12} />Save to notes</button>}</div>)}
              {chatting && <><div className="message user"><div className="message-author">You</div><p>{pendingQuestion}</p></div><div className="thinking"><LoaderCircle className="spin" size={15} />Working with your lecture…</div></>}
              <div ref={chatEnd} />
            </div>
            <div className="composer-area"><form className="composer" onSubmit={event => { event.preventDefault(); void send(); }}><textarea aria-label="Ask about this slide" placeholder="What’s confusing on this slide?" value={question} maxLength={6000} onChange={event => setQuestion(event.target.value)} disabled={chatting} onKeyDown={event => { if (event.key === 'Enter' && !event.shiftKey) { event.preventDefault(); void send(); } }} /><div><span><FileText size={12} />Slide {page} attached</span><button className="send-button" aria-label="Send question" disabled={!question.trim() || chatting}>{chatting ? <LoaderCircle className="spin" size={17} /> : <ArrowUp size={19} />}</button></div></form><p>Answers should cite your slides. Check anything that seems off.</p></div>
          </> : <div className="notes-panel"><div className="notes-heading"><div><h3>Your thoughts, kept here.</h3><p>Pick up where you left off on slide {page}.</p></div><PencilLine size={19} /></div><textarea className="notes-editor" aria-label="Slide notes" placeholder={"Write it in your own words…\n\nKey idea:\nWhat I’m still wondering:"} value={work.notes} maxLength={30000} onChange={event => updateNotes(event.target.value)} onBlur={() => void flushNotes().catch(reason => setError(reason.message))} /><div className={`notes-status ${notesStatus === 'error' ? 'error' : ''}`} role="status">{notesStatus === 'saved' ? <><Check size={13} />Saved</> : notesStatus === 'saving' ? <><LoaderCircle className="spin" size={13} />Saving…</> : notesStatus === 'error' ? <button onClick={() => void flushNotes().catch(reason => setError(reason.message))}>Couldn’t save · retry</button> : 'Unsaved changes'}</div>
            {work.marks.length > 0 && <div className="annotation-list"><div className="eyebrow">ON YOUR SLIDE</div>{work.marks.map((mark, index) => <div className="annotation-item" key={mark.id}><span>{mark.kind === 'pin' ? <Pin size={14} /> : <Highlighter size={14} />}</span><div>{mark.kind === 'pin' ? <input aria-label={`Text for pinned note ${work.marks.slice(0, index + 1).filter(item => item.kind === 'pin').length}`} placeholder="What would you like to remember?" defaultValue={mark.text} maxLength={1000} disabled={busy} onBlur={event => { if (event.target.value !== mark.text) void persistMarks(work.marks.map(item => item.id === mark.id ? { ...item, text: event.target.value } : item)); }} /> : <span>Highlighted region</span>}</div><button aria-label={`Delete annotation ${index + 1}`} disabled={busy} onClick={() => void persistMarks(work.marks.filter(item => item.id !== mark.id))}><Trash2 size={13} /></button></div>)}</div>}
            <button className="outline-button export-notes" disabled={!work.notes && !work.marks.some(mark => mark.text)} onClick={exportNotes}><ArrowDownToLine size={15} />Export this slide’s notes</button>
          </div>}
        </aside>
      </div></>}
    </main>
    {connectionModal && <div className="modal-backdrop" onClick={() => setConnectionModal(false)}><section ref={connectionDialog} className="connection-modal" role="dialog" aria-modal="true" aria-labelledby="connection-title" onClick={event => event.stopPropagation()}><button className="icon-button modal-close" aria-label="Close connection information" onClick={() => setConnectionModal(false)}><X size={19} /></button><div className="buddy-emblem"><Sparkles size={23} /></div><span className="eyebrow">YOUR STUDY COMPANION</span><h2 id="connection-title">{health?.tutor_configured ? 'Your tutor connection is configured.' : 'Bring your tutor online.'}</h2><p>{health?.tutor_configured ? 'Questions use the current slide, nearby slides, relevant excerpts, and this slide’s conversation.' : 'Start the local model using the project’s setup instructions. It runs on this machine with no API key or per-question fee. The model must be downloaded once before the first session.'}</p><div className="privacy-note"><BookOpen size={18} /><span>Your lecture content and conversations stay on this machine. The local tutor can read slide images as well as text. Check equations and answers against the original slide.</span></div><p className="small muted">The viewer, notes, and guided visual lab work without this connection. This is an early personal workspace.</p><button className="primary-button" onClick={() => void refreshConnection()}>Check connection settings<ArrowRight size={16} /></button></section></div>}
  </div>;
}

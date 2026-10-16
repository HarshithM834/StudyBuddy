import { useState } from 'react';
import { ArrowRight, Check, RotateCcw, X } from 'lucide-react';
import type { Visual } from './types';

export function ConceptDiagram({ visual }: { visual: Visual }) {
  const nodes = visual.nodes.slice(0, 7);
  const ids = new Set(nodes.map(node => node.id));
  const edges = visual.edges.filter(edge => ids.has(edge.source) && ids.has(edge.target));
  return <section className="concept-diagram" aria-label={visual.title}>
    <div className="eyebrow">Visual explanation</div>
    <h4>{visual.title}</h4>
    <div className="diagram-nodes">{nodes.map((node, i) => <div key={node.id}><span>{i + 1}</span>{node.label}</div>)}</div>
    <div className="diagram-edges">{edges.map((edge, i) => <div key={i}>
      <b>{nodes.find(node => node.id === edge.source)?.label}</b><ArrowRight size={14} aria-hidden="true" /><b>{nodes.find(node => node.id === edge.target)?.label}</b>
      {edge.label && <small>{edge.label}</small>}
    </div>)}</div>
  </section>;
}

export default function VisualLab({ onClose }: { onClose: () => void }) {
  const [flipped, setFlipped] = useState<number | null>(2);
  const sent = [1, 1, 0, 1, 1, 0, 0];
  const labels = ['A', 'B', 'C', 'D', 'X', 'Y', 'Z'];
  const groups = [[0, 1, 3], [0, 2, 3], [1, 2, 3]];
  const received = sent.map((bit, i) => bit ^ Number(i === flipped));
  const calculated = groups.map(group => group.reduce((value, i) => value ^ received[i], 0));
  const failed = calculated.map((value, i) => value !== received[i + 4]);
  const syndrome = failed.map(Number).join('');
  const lookup: Record<string, string> = { '110': 'A', '101': 'B', '011': 'C', '111': 'D', '100': 'X', '010': 'Y', '001': 'Z' };
  const identified = lookup[syndrome];
  return <section className="visual-lab" aria-label="Hamming visual lab">
    <header><div><span className="eyebrow">Interactive example · From your lecture</span><h3>One bit changes. Which checks notice?</h3></div><button className="icon-button" aria-label="Close visual lab" onClick={onClose}><X size={18} /></button></header>
    <p>Choose a bit to flip. This uses your slide’s <strong>ABCD | XYZ</strong> layout and assumes at most one error.</p>
    <div className="lab-bits">{received.map((bit, i) => <button key={i} onClick={() => setFlipped(i)} aria-pressed={flipped === i} aria-label={`Flip bit ${labels[i]}`} className={`${i > 3 ? 'parity' : ''} ${flipped === i ? 'flipped' : ''}`}>
      <span>{labels[i]}</span><strong>{bit}</strong><small>{flipped === i ? 'changed' : i > 3 ? 'check' : 'data'}</small>
    </button>)}</div>
    <div className="lab-checks">{groups.map((group, i) => <div key={i} className={failed[i] ? 'failed' : 'passed'}>
      <strong>{labels[i + 4]}</strong><span>{group.map(j => labels[j]).join(' ⊕ ')}</span><span>{failed[i] ? <X size={15} /> : <Check size={15} />}{failed[i] ? 'Fails' : 'Passes'}</span>
    </div>)}</div>
    <div className="lab-result">{!identified ? 'All checks agree. No correction is needed under our single-error assumption.' : identified === 'C' ? 'Y and Z fail; X passes. Both C and D affect Y and Z, but D would also fail X. That identifies C.' : `This pattern identifies ${identified}. ${identified === 'D' ? 'D is included in all three checks.' : ['X', 'Y', 'Z'].includes(identified) ? 'Only that check bit changed; the message bits are intact.' : `${identified} affects ${failed.flatMap((v, i) => v ? [labels[i + 4]] : []).join(' and ')}.`}`}</div>
    <button className="text-button" onClick={() => setFlipped(null)}><RotateCcw size={13} />Reset to no error</button>
    <small className="lab-source">PDF pages 21–23 · Guided example, available without the AI tutor</small>
  </section>;
}

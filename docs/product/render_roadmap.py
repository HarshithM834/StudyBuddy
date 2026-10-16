"""Regenerate the documentation-only timeline with Matplotlib (not an app dependency)."""
from datetime import datetime
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

HERE = Path(__file__).resolve().parent
date = lambda value: mdates.date2num(datetime.fromisoformat(value))
phases = [
    ('P0  Workspace foundation', '2026-10-14', '2026-10-16', '#4e8062', None, 'Cloud foundation checked; Mac and tutor gates open'),
    ('P1  Menu-bar companion MVP', '2026-10-15', '2026-10-19', '#285f48', None, 'Target Oct 18 · requires PRD gates G1–G4'),
    ('P2  Limited pilot', '2026-10-19', '2026-10-26', '#8793bc', '//', 'Conditional on MVP readiness · 3–5 students'),
    ('P3  Repeat-study iteration', '2026-10-26', '2026-11-09', '#8793bc', '//', 'Scope chosen from observed reuse'),
    ('P4  Course-context discovery', '2026-11-09', '2026-11-23', '#a9afa9', '..', 'Discovery only; no delivery date'),
]
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'svg.fonttype':'none'})
fig, ax = plt.subplots(figsize=(16, 6.4))
fig.patch.set_facecolor('#f8faf6')
ax.set_facecolor('#f8faf6')
for index, (label, start, end, color, hatch, note) in enumerate(phases):
    ax.barh(index, date(end)-date(start), left=date(start), height=.45,
            color=color, edgecolor='#f8faf6', linewidth=1.2, hatch=hatch)
    if index < 3:
        ax.text(date(end)+.45, index, note, va='center', fontsize=10, color='#31463d')
    else:
        ax.text(date(start)+.5, index, note, va='center', fontsize=10, color='#172a22')
ax.set_yticks(range(len(phases)), [item[0] for item in phases])
ax.invert_yaxis()
ax.set_xlim(date('2026-10-13'), date('2026-11-24'))
ax.set_ylim(4.7,-.8)
ticks=['2026-10-14','2026-10-18','2026-10-26','2026-11-02','2026-11-09','2026-11-16','2026-11-23']
ax.set_xticks([date(t) for t in ticks], [datetime.fromisoformat(t).strftime('%b %d') for t in ticks])
ax.tick_params(axis='both',length=0,pad=12,labelcolor='#41574a')
ax.grid(axis='x',color='#e0e6dc',linewidth=.8)
ax.set_axisbelow(True)
for spine in ax.spines.values():spine.set_visible(False)
ax.axvline(date('2026-10-18'),color='#b27336',linestyle=(0,(3,4)),linewidth=1.1,zorder=0)
fig.text(.055,.94,'STUDYBUDDY  /  PRODUCT ROADMAP',fontsize=20,weight='bold',color='#203d2c')
fig.text(.055,.887,'As of Oct 16, 2026 · America/New_York · Later windows depend on evidence and release gates',fontsize=11,color='#526557')
fig.legend(handles=[Patch(facecolor='#4e8062',label='Observed foundation'),Patch(facecolor='#285f48',label='Current delivery target'),Patch(facecolor='#8793bc',hatch='//',label='Conditional window'),Patch(facecolor='#a9afa9',hatch='..',label='Discovery')],loc='lower left',bbox_to_anchor=(.05,.12),ncol=4,frameon=False,fontsize=10)
fig.text(.055,.095,'P5  UNSCHEDULED VISION  ·  permitted lecture capture, concept maps, anchored drawing, broader app/voice help, and adaptive practice',fontsize=10,color='#41574a')
fig.text(.055,.047,'A working local model connection is not release readiness. Incorrect tutoring feedback remains a blocker.',fontsize=10,color='#815528')
fig.subplots_adjust(left=.22,right=.96,top=.82,bottom=.255)
fig.savefig(HERE/'roadmap-timeline.png',dpi=160,facecolor=fig.get_facecolor())
fig.savefig(HERE/'roadmap-timeline.svg',facecolor=fig.get_facecolor())
plt.close(fig)

# Keep generated SVG paths whitespace-clean for source control.
svg_path = HERE / "roadmap-timeline.svg"
svg_path.write_text("\n".join(line.rstrip() for line in svg_path.read_text().splitlines()) + "\n")

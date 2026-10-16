"""UI integration check with a simulated native bridge and model; never a Mac or quality acceptance test."""
import asyncio, base64, io, json, os, shutil
from pathlib import Path
from PIL import Image
from playwright.async_api import async_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / '.studybuddy/checks'
OUT.mkdir(parents=True, exist_ok=True)
BASE = os.environ.get('STUDYBUDDY_TEST_URL', 'http://127.0.0.1:8004')
from urllib.parse import urlsplit
assert urlsplit(BASE).hostname in {'127.0.0.1', 'localhost', '::1'}, 'Use a local isolated test server.'
async def main():
 image=io.BytesIO();Image.new('RGB',(320,200),'#e6eddc').save(image,'JPEG')
 image='data:image/jpeg;base64,'+base64.b64encode(image.getvalue()).decode()
 native="""window.webkit={messageHandlers:{studybuddy:{postMessage:({action})=>{
 window.nativeActions=(window.nativeActions||[]).concat(action);
 if(action==='start'||action==='pause') window.dispatchEvent(new CustomEvent('studybuddy:screen',{detail:{type:'status',active:action==='start',message:action==='start'?'Following your active window':'Paused · screen capture stopped'}}));
 }}}};"""
 async with async_playwright() as p:
  browser=await p.chromium.launch(headless=True,executable_path=shutil.which('chromium'))
  page=await browser.new_page(viewport={'width':430,'height':740})
  await page.add_init_script(native)
  errors=[];page.on('pageerror',lambda error: errors.append(str(error)))
  external=[]
  async def block_external(route):
   external.append(route.request.url);await route.abort()
  await page.route('https://example.com/**',block_external)
  messages={};notes={};gate=asyncio.Event();chat_count=0
  async def route_api(route):
   nonlocal chat_count
   path=route.request.url.split('/api')[-1]
   if path=='/documents': data=[{'id':'lecture','name':'CYSE 425 Week 6.pdf','page_count':44,'course':'CYSE 425','example':None}]
   elif path.endswith('/follow/prepare'): data={'ready':True}
   elif path.endswith('/follow/match'):
    text=route.request.post_data_json['text'];n=22 if 'parity' in text else 23 if 'syndrome' in text else None
    data={'page':n,'status':'matched' if n else 'unknown'}
   elif path.endswith('/chat'):
    chat_count+=1;body=route.request.post_data_json; await gate.wait()
    key=path[:-5]
    result=[{'id':'u','role':'user','content':body['message'],'citations':[],'visual':None}, {'id':'a','role':'assistant','content':'Saved explanation for the earlier parity slide. ![untrusted image](https://example.com/tracker)','citations':[22],'visual':None}]
    messages[key]=result;data={'messages':result}
   elif path.endswith('/work'):
    key=path[:-5];data={'notes':notes.get(key,''),'marks':[],'messages':messages.get(key,[])}
   elif path.endswith('/notes'):
    notes[path[:-6]]=route.request.post_data_json['text'];data={'saved':True}
   elif path.startswith('/companion/contexts'): data={'messages':[]}
   elif '/image?' in path: return await route.fulfill(content_type='image/jpeg', body=base64.b64decode(image.split(',')[1]))
   else: return await route.continue_()
   await route.fulfill(json=data)
  await page.route('**/api/**',route_api)
  await page.goto(BASE + '/?companion=1')
  await expect(page.get_by_role('heading',name='Right here, as you study.')).to_be_visible()
  await page.get_by_role('button',name='Turn on study mode',exact=True).click()
  await page.locator('summary').click()
  await page.get_by_label('Course PDF context').select_option('lecture')
  await expect(page.get_by_label('Explain as I go · recognized PDF slides')).to_be_visible()
  async def frame(text,app='Safari',title='Canvas — CYSE 425'):
   await page.evaluate("detail=>window.dispatchEvent(new CustomEvent('studybuddy:screen',{detail}))",{'type':'frame','application':app,'title':title,'text':text,'image':image,'capturedAt':1})
   await page.wait_for_timeout(150)
  await frame('parity data bits even count lecture check rule')
  await frame('parity data bits even count lecture check rule')
  await expect(page.locator('.current-context strong')).to_have_text('PDF slide 22')
  question=page.get_by_role('textbox',name='Ask about what you are viewing')
  await question.fill('Help with this parity check.')
  await page.get_by_role('button',name='Send question',exact=True).click()
  await expect(page.locator('.companion-pending')).to_contain_text('PDF slide 22')
  await frame('syndrome identifies the erroneous bit using failed checks')
  await frame('syndrome identifies the erroneous bit using failed checks')
  await expect(page.locator('.current-context strong')).to_have_text('PDF slide 23')
  await expect(question).to_have_value('')
  gate.set()
  await expect(page.locator('.companion-pending')).to_have_count(0)
  await expect(page.locator('.message.assistant')).to_have_count(0)
  await expect(page.locator('.companion-notice')).to_contain_text('Answer saved for PDF slide 22')
  await frame('parity data bits even count lecture check rule')
  await frame('parity data bits even count lecture check rule')
  await expect(page.locator('.message.assistant')).to_contain_text('Saved explanation for the earlier parity slide.')
  await page.get_by_role('button',name='Save to slide notes',exact=True).click()
  await expect(page.locator('.companion-notes')).to_contain_text('Saved explanation')
  await page.get_by_role('button',name='Page 22',exact=True).click()
  await expect(page.get_by_alt_text('Source PDF page 22')).to_be_visible()
  await page.wait_for_function('document.querySelector(".source-preview img")?.naturalWidth > 0')
  await page.get_by_role('button',name='Close source · PDF page 22').click()
  # Switching apps is automatic; no app selector is present.
  await question.fill('Keep my draft on this slide.')
  await page.evaluate("window.dispatchEvent(new CustomEvent('studybuddy:screen',{detail:{type:'changing',message:'Following active app…'}}))")
  await frame('Introduction video instructor channel subscribe lecture description',app='Chrome',title='YouTube — RF overview')
  await expect(page.locator('.current-context strong')).to_have_text('YouTube — RF overview')
  await expect(page.locator('.current-context small')).to_contain_text('no audio')
  await expect(page.locator('.message.assistant')).to_have_count(0)
  await frame('parity data bits even count lecture check rule')
  await frame('parity data bits even count lecture check rule')
  await expect(question).to_have_value('Keep my draft on this slide.')
  await page.get_by_label('Explain as I go · recognized PDF slides').check()
  await frame('syndrome identifies the erroneous bit using failed checks')
  await frame('syndrome identifies the erroneous bit using failed checks')
  await page.wait_for_timeout(2300)
  assert chat_count==2,chat_count
  await frame('syndrome identifies the erroneous bit using failed checks')
  await page.wait_for_timeout(2200)
  assert chat_count==2,chat_count
  await page.get_by_role('button',name='Pause study mode',exact=True).click()
  await frame('parity data bits even count lecture check rule')
  await expect(page.locator('.current-context')).to_have_count(0)
  await expect(page.get_by_label('Explain as I go · recognized PDF slides')).not_to_be_checked()
  # Resume to a representative captured-view UI for the artifact.
  await page.get_by_role('button',name='Start study mode',exact=True).click()
  await frame('parity data bits even count lecture check rule')
  await frame('parity data bits even count lecture check rule')
  await expect(page.locator('.message.assistant')).to_have_count(1)
  assert await page.evaluate('document.documentElement.scrollWidth <= innerWidth')
  await page.screenshot(path=str(OUT/'companion-panel-test.png'))
  assert not errors,errors
  assert not external,external
  await browser.close()
  print('PASS: simulated native bridge; cross-app context, two-frame PDF match, late-answer isolation, restored history/notes/drafts, source view, single auto-explain, pause ignores late capture; no JS errors or horizontal overflow. Actual macOS capture and model quality not tested.')
asyncio.run(main())

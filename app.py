"""Story-led v2.1. The worksheet is optional; the economic decision is central."""
from pathlib import Path
import ast
import math
import json
import hashlib
import operator
import pandas as pd
import streamlit as st
from story import chapters, F, D, K, BACK, KB, HIGH, KH, PV
from lessons import (forward_strip,equal_swap,unequal_swap,settlements,curve_changes,
                     single_payment,replacement,mismatch,carry_lesson,extrapolation,scratchpad)

ROOT=Path(__file__).parent
STORY=chapters()
st.set_page_config(page_title='Riverside · Commodity Swap Studio',page_icon='🛢️',layout='centered')
st.markdown('''<style>
.stApp{background:#fcfefd;color:#123e4c}.block-container{max-width:980px;padding-top:2rem}
h1,h2,h3{color:#0a5860!important}h1{font-size:2rem!important}h2{font-size:1.35rem!important}
[data-testid="stSidebar"]{background:#eaf5f1}.objective{padding:12px 16px;border-left:4px solid #078474;background:#e8f8f1;border-radius:6px;margin-bottom:20px}
[data-testid="stCaptionContainer"] p{color:#235b70!important}.stButton>button{border-radius:8px}
th{font-weight:650!important;color:#124c58!important;background:#edf6f3!important}
</style>''',unsafe_allow_html=True)

from studio_theme import apply_studio_theme, style_plotly, studio_line_chart, WORKSHEET_CSS
apply_studio_theme()


def prose(text):st.markdown(text.replace('$',r'\$'))


def calculate(text):
    """Restricted arithmetic for the small student task; no arbitrary evaluation."""
    source=text.strip().removeprefix('=').strip().replace(',','').translate(str.maketrans({'×':'*','÷':'/','−':'-'}))
    if not source or len(source)>150:raise ValueError('Enter a number or a short calculation.')
    tree=ast.parse(source,mode='eval')
    def visit(node,depth=0):
        if depth>20:raise ValueError('Use a shorter calculation.')
        if isinstance(node,ast.Expression):return visit(node.body,depth+1)
        if isinstance(node,ast.Constant) and type(node.value) in (int,float):return float(node.value)
        if isinstance(node,ast.UnaryOp) and isinstance(node.op,(ast.UAdd,ast.USub)):
            return visit(node.operand,depth+1)*(1 if isinstance(node.op,ast.UAdd) else -1)
        if isinstance(node,ast.BinOp) and type(node.op) in (ast.Add,ast.Sub,ast.Mult,ast.Div):
            return {ast.Add:operator.add,ast.Sub:operator.sub,ast.Mult:operator.mul,ast.Div:operator.truediv}[type(node.op)](visit(node.left,depth+1),visit(node.right,depth+1))
        if isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id.upper() in ('EXP','LN') and len(node.args)==1 and not node.keywords:
            return (math.exp if node.func.id.upper()=='EXP' else math.log)(visit(node.args[0],depth+1))
        raise ValueError('Use numbers, + − * /, parentheses, EXP or LN. Cell references belong in the optional worksheet.')
    value=visit(tree)
    if not math.isfinite(value):raise ValueError('The answer must be finite.')
    return value


def preview(raw):
    if not raw.strip():return
    try:st.caption(f'Calculated result: {calculate(raw):,.6f}'.rstrip('0').rstrip('.'))
    except (ValueError,SyntaxError,ZeroDivisionError,OverflowError):
        st.caption('Could not calculate this entry. Check the arithmetic; division by zero is not allowed.')


def grid(headers,rows):
    def fmt(x):
        if isinstance(x,(int,float)):
            return f'{x:,.4f}'.rstrip('0').rstrip('.') if x%1 else f'{x:,.0f}'
        return str(x)
    st.table(pd.DataFrame([[fmt(x) for x in row] for row in rows],columns=headers))


# Bundled fallback keeps cloud deployments functional if non-Python assets are omitted.
BUNDLED_WORKSHEET = '<!doctype html><html lang="en"><head><meta charset="utf-8"><style>\n*{box-sizing:border-box}body{font:15px system-ui,sans-serif;color:#123b4a;margin:0;background:white;padding:4px 2px}button,input{font:inherit}button{border:1px solid #147c78;background:white;color:#075d59;border-radius:6px;padding:8px 12px;cursor:pointer}button:hover{background:#dff7f1}button:focus-visible,input:focus-visible,select:focus-visible{outline:3px solid #b95213;outline-offset:1px}button.primary{background:#09665f;color:white}button:disabled{opacity:.5;cursor:default}.toolbar{display:flex;gap:7px;flex-wrap:wrap;margin:10px 0}.formula{display:flex;gap:8px;align-items:center;background:#edf6fc;padding:9px;border-radius:7px}.formula input{flex:1;min-width:100px;padding:8px;border:1px solid #367aa0;border-radius:4px}.address{min-width:42px;font-weight:750}.gridwrap{overflow:auto;border:1px solid #74a3af;border-radius:7px;margin:10px 0}table{border-collapse:collapse;width:100%;min-width:560px;table-layout:fixed}th,td{border:1px solid #b2cbd0;padding:0;text-align:right}th{background:#123f50;color:white;padding:9px;font-weight:650;text-align:center;font-size:13px}th.rownum{width:40px;background:#edf6fc;color:#123f50}td input{width:100%;border:0;min-width:70px;padding:11px 6px;text-align:right;background:#fff9db;color:#123b4a;font-variant-numeric:tabular-nums}td input[readonly]{background:#edf6fc;font-weight:550}td input.textcell{text-align:left}td.selected{outline:3px solid #da731c;outline-offset:-3px}td.ok input{background:#ddf5e9}td.bad input{background:#ffebe4}.legend{line-height:1.55;margin:8px 0}.msg{padding:12px;border-left:4px solid #188178;background:#e9f8f2;margin:8px 0;white-space:pre-wrap;line-height:1.5}.msg.error{border-color:#b74121;background:#fff1e9}.msg:empty{display:none}details{margin-top:10px}summary{cursor:pointer;color:#075d59;font-weight:650}p{line-height:1.5;margin:8px 0}.rowhelp{font-weight:600;color:#124e77}code{background:#edf6fc;padding:2px 4px}#status{min-height:22px}#worktitle{font-size:18px;font-weight:750;margin:2px 0 8px} .small{font-size:13px}\n</style></head><body>\n<div id="worktitle"></div><p id="instructions"></p>\n<div class="legend small">Blue cells are given. Yellow cells are yours. Click a yellow cell, type a number or formula, with or without a leading =, then press Enter or click outside. The cell displays the calculated result.</div>\n<div class="formula"><span class="address" id="address">Cell</span><input id="formula" aria-label="Formula bar" placeholder="Select a yellow cell to begin"><button id="apply">Apply</button></div>\n<div class="gridwrap"><table id="grid" aria-label="Calculation worksheet"></table></div>\n<div class="rowhelp" id="rowhelp"></div>\n<div class="toolbar"><button id="fill">Fill down from selected cell</button><button class="primary" id="step">Check selected row</button><button id="check">Check worksheet</button><button id="hint">Next hint for selected cell</button><button id="show">Show selected step</button><button id="solution">Reveal worked solution</button><button id="reset">Reset worksheet</button></div>\n<div id="status" role="status" aria-live="polite"></div><div id="feedback" class="msg" role="status"></div><div id="hints" class="msg"></div>\n<details><summary>Spreadsheet help and keyboard shortcuts</summary><p>A leading = is optional in every calculation. Use <code>B1*C1</code> or <code>=B1*C1</code>, <code>=SUM(C1:C4)</code>, <code>=EXP(-B1*A1)</code>, or <code>=LN(B1/C1)</code>. Supported: + − * / ^, parentheses, percentages, SUM, AVERAGE, MIN, MAX, EXP, LN, ABS, SQRT, ROUND. Rates are decimals: 4% = 0.04.</p><p>Enter commits a cell and moves down. Tab moves across. Select a formula cell and use Fill down; relative references advance, while <code>$B$1</code> remains fixed. Fill down stops at the first locked cell. Paste a rectangular block of numbers or formulas from the clipboard; locked cells are skipped. Blanks are reported as missing inputs, never silently treated as zero.</p><p>References start at row 1 of the data (the column headings are not a spreadsheet row). Results display up to six decimals and calculations keep full precision. Formula bar shows the underlying formula. Work is kept only in this browser tab\'s session when browser storage is available. No grades are sent. Reset clears this worksheet only.</p></details>\n<script>/*ENGINE*/</script><script>\nconst cfg=/*CONFIG*/;\nconst S=SheetMath,$=id=>document.getElementById(id);let raw={},selected=null,hintLevels={},attempted=false;\nconst storageKey=\'commodity-v2:\'+cfg.id;\ntry{const saved=JSON.parse(sessionStorage.getItem(storageKey)||\'null\');if(saved){raw=saved.raw||{};attempted=!!saved.attempted;}}catch(e){}\nconst refs=Object.keys(cfg.cells), editable=refs.filter(k=>!cfg.cells[k].locked);\nfor(const ref of refs)if(cfg.cells[ref].locked||raw[ref]===undefined)raw[ref]=String(cfg.cells[ref].value??\'\');\nfunction save(){try{sessionStorage.setItem(storageKey,JSON.stringify({raw,attempted}));}catch(e){$(\'status\').textContent=\'Session storage unavailable. Keep this worksheet open to retain work.\';}}\nfunction read(ref){if(!(ref in raw))throw Error(\'Reference \'+ref+\' is outside this worksheet\');if(cfg.cells[ref].text)throw Error(ref+\' is a label, not a number\');return raw[ref];}\nfunction result(ref){return S.evaluate(raw[ref],read,[ref]);}\nfunction display(ref){if(cfg.cells[ref].text)return raw[ref];if(!raw[ref].trim())return \'\';try{return result(ref).toLocaleString(\'en-US\',{maximumFractionDigits:6,useGrouping:false});}catch(e){return \'#CHECK\';}}\nfunction clearFeedback(){for(const el of document.querySelectorAll(\'td\'))el.classList.remove(\'ok\',\'bad\');$(\'feedback\').textContent=\'\';$(\'hints\').textContent=\'\';}\nfunction renderValues(){for(const ref of refs){const el=document.querySelector(\'[data-ref="\'+ref+\'"]\');if(el&&document.activeElement!==el)el.value=display(ref);}save();}\nfunction select(ref){selected=ref;for(const td of document.querySelectorAll(\'td\'))td.classList.remove(\'selected\');const el=document.querySelector(\'[data-ref="\'+ref+\'"]\');el.parentElement.classList.add(\'selected\');$(\'address\').textContent=ref;$(\'formula\').value=raw[ref];$(\'formula\').disabled=cfg.cells[ref].locked;$(\'apply\').disabled=cfg.cells[ref].locked;const r=S.coordinate(ref)[0];$(\'rowhelp\').textContent=cfg.rowGuides[r]||\'\';$(\'hints\').textContent=\'\';}\nfunction commit(ref,value){if(cfg.cells[ref].locked)return;if(raw[ref]!==value)clearFeedback();raw[ref]=value;attempted=attempted||value.trim()!==\'\';renderValues();if(selected===ref)$(\'formula\').value=value;try{$(\'status\').textContent=value.trim()?ref+\' = \'+display(ref):ref+\' is blank.\';result(ref);}catch(e){$(\'status\').textContent=ref+\': \'+e.message;}}\nfunction focusCell(ref){const el=document.querySelector(\'[data-ref="\'+ref+\'"]\');if(el){el.focus();el.select();}}\n$(\'worktitle\').textContent=cfg.title;$(\'instructions\').textContent=cfg.instructions;\nconst tr=document.createElement(\'tr\');const corner=document.createElement(\'th\');corner.className=\'rownum\';corner.textContent=\'#\';tr.appendChild(corner);\ncfg.headers.forEach((h,c)=>{const th=document.createElement(\'th\');th.textContent=S.colName(c)+\' · \'+h;tr.appendChild(th);});$(\'grid\').appendChild(tr);\nfor(let r=0;r<cfg.rows;r++) {const tr=document.createElement(\'tr\'),th=document.createElement(\'th\');th.className=\'rownum\';th.textContent=r+1;tr.appendChild(th);\n for(let c=0;c<cfg.headers.length;c++){const ref=S.colName(c)+(r+1),cell=cfg.cells[ref],td=document.createElement(\'td\'),el=document.createElement(\'input\');el.dataset.ref=ref;el.setAttribute(\'aria-label\',ref+\' \'+cfg.headers[c]);el.readOnly=cell.locked;el.spellcheck=false;el.value=display(ref);if(cell.text)el.className=\'textcell\';\n el.addEventListener(\'focus\',()=>{select(ref);if(!cell.locked){el.value=raw[ref];el.select();}});\n el.addEventListener(\'blur\',()=>{if(!cell.locked)commit(ref,el.value);el.value=display(ref);});\n el.addEventListener(\'keydown\',e=>{if(e.key===\'Enter\'){e.preventDefault();commit(ref,el.value);el.blur();const next=S.colName(c)+(r+2);if(cfg.cells[next]&&!cfg.cells[next].locked)focusCell(next);}if(e.key===\'Escape\'){el.value=raw[ref];el.blur();}});\n el.addEventListener(\'paste\',e=>{const text=e.clipboardData.getData(\'text\');if(!/[\\t\\n]/.test(text))return;e.preventDefault();text.trimEnd().split(/\\r?\\n/).forEach((row,dr)=>row.split(\'\\t\').forEach((val,dc)=>{const target=S.colName(c+dc)+(r+dr+1);if(cfg.cells[target]&&!cfg.cells[target].locked)raw[target]=val;}));attempted=true;el.value=raw[ref];clearFeedback();renderValues();});td.appendChild(el);tr.appendChild(td);}$(\'grid\').appendChild(tr);}\n$(\'apply\').onclick=()=>{if(selected)commit(selected,$(\'formula\').value);};$(\'formula\').onkeydown=e=>{if(e.key===\'Enter\')$(\'apply\').click();};\n$(\'fill\').onclick=()=>{if(!selected||cfg.cells[selected].locked){$(\'feedback\').textContent=\'Select an editable cell containing a number or formula first.\';return;}const [r,c]=S.coordinate(selected);let n=0;for(let j=r+1;j<cfg.rows;j++){const dest=S.colName(c)+(j+1);if(cfg.cells[dest].locked)break;raw[dest]=S.shift(raw[selected],j-r);n++;}clearFeedback();renderValues();$(\'feedback\').textContent=\'Filled \'+n+\' cell(s). Select each cell to inspect its formula.\';};\nfunction check(targets){attempted=true;save();let correct=0,missing=0,wrong=[];for(const ref of targets){const cell=cfg.cells[ref];if(cell.expected===undefined)continue;const td=document.querySelector(\'[data-ref="\'+ref+\'"]\')?.parentElement;td?.classList.remove(\'ok\',\'bad\');if(!raw[ref].trim()){missing++;wrong.push(ref+\': still blank.\');continue;}try{const val=result(ref),tol=cell.tolerance??Math.max(0.00002,Math.abs(cell.expected)*0.00002);if(Math.abs(val-cell.expected)<=tol){correct++;td?.classList.add(\'ok\');}else{td?.classList.add(\'bad\');wrong.push(ref+\': recheck \'+(cell.process||\'the formula, inputs and units\')+\'.\');}}catch(e){td?.classList.add(\'bad\');wrong.push(ref+\': \'+e.message+\'.\');}}\n const count=targets.filter(k=>cfg.cells[k].expected!==undefined).length;$(\'feedback\').className=\'msg\'+(wrong.length?\' error\':\'\');$(\'feedback\').textContent=count===0?\'This is a free scratchpad: formulas calculate automatically. There is no target answer.\':wrong.length?correct+\' of \'+count+\' calculation cells correct. \'+missing+\' blank.\\n\'+wrong.join(\'\\n\'):\'All \'+count+\' calculation cells checked correctly. \'+cfg.interpretation;}\n$(\'check\').onclick=()=>check(editable);$(\'step\').onclick=()=>{if(!selected){$(\'feedback\').textContent=\'Select a cell in the row you want to check.\';return;}const r=S.coordinate(selected)[0];check(editable.filter(k=>S.coordinate(k)[0]===r));};\n$(\'hint\').onclick=()=>{if(!selected||cfg.cells[selected].locked){$(\'hints\').textContent=\'Select a yellow calculation cell first.\';return;}const cell=cfg.cells[selected];const hints=[cell.process||\'Use the given inputs and the formula above.\',cell.hint||\'Build the expression one operation at a time.\',cell.formula?\'Spreadsheet formula: \'+cell.formula:\'Try =SUM(A1:A3) after entering numbers in A1:A3.\'];const level=hintLevels[selected]||0;$(\'hints\').textContent=selected+\' · Hint \'+(Math.min(level,2)+1)+\' of 3: \'+hints[Math.min(level,2)];hintLevels[selected]=Math.min(level+1,2);};\n$(\'show\').onclick=()=>{if(!selected||!cfg.cells[selected].formula){$(\'feedback\').textContent=\'Select a yellow calculation cell with a guided step.\';return;}if(!attempted){$(\'feedback\').textContent=\'Try a calculation or check your worksheet first. You can also request the full worked solution.\';return;}const cell=cfg.cells[selected];$(\'hints\').textContent=selected+\': \'+cell.formula+\' → \'+cell.expected.toLocaleString(\'en-US\',{maximumFractionDigits:6})+\'. \'+cell.process;};\n$(\'solution\').onclick=()=>{$(\'hints\').textContent=\'Worked solution (your entries are preserved):\\n\'+editable.filter(k=>cfg.cells[k].formula).map(k=>k+\'  \'+cfg.cells[k].formula+\'  = \'+cfg.cells[k].expected.toLocaleString(\'en-US\',{maximumFractionDigits:6})).join(\'\\n\')+\'\\n\'+cfg.interpretation;};\n$(\'reset\').onclick=()=>{for(const ref of editable)raw[ref]=\'\';hintLevels={};attempted=false;clearFeedback();renderValues();if(selected)$(\'formula\').value=raw[selected];$(\'status\').textContent=\'Worksheet reset. Try again from the first yellow cell.\';};\nif(editable.length)select(editable[0]);\n</script></body></html>\n'
BUNDLED_ENGINE = "/* Small, offline spreadsheet engine. Never evaluates JavaScript or arbitrary code. */\n(function(root) {\n  'use strict';\n  function colIndex(s) { let n=0; for(const c of s.toUpperCase()) n=n*26+c.charCodeAt(0)-64; return n-1; }\n  function colName(n) { let s=''; for(n++;n;n=Math.floor((n-1)/26)) s=String.fromCharCode(65+(n-1)%26)+s; return s; }\n  function coordinate(ref) { const m=/^\\$?([A-Z]+)\\$?([1-9]\\d*)$/i.exec(ref); if(!m) throw Error('Invalid cell reference'); return [Number(m[2])-1,colIndex(m[1])]; }\n  function evaluate(raw, ref, stack=[]) {\n    const text=String(raw??'').trim().replace(/×/g,'*').replace(/÷/g,'/').replace(/−/g,'-');\n    if(!text) throw Error('Blank cell: enter a number or formula');\n    if(text.length>600) throw Error('Formula is too long');\n    if(text[0]!=='=') { const v=Number(text.replace(/,/g,'')); if(Number.isFinite(v)) return v; }\n    const src=(text[0]==='='?text.slice(1):text).toUpperCase(); let tokens=[],pos=0;\n    while(pos<src.length) {\n      if(/\\s/.test(src[pos])) {pos++;continue;}\n      const m=/^(\\$?[A-Z]+\\$?[1-9]\\d*|(?:\\d+\\.?\\d*|\\.\\d+)(?:E[+-]?\\d+)?|[A-Z]+|[+\\-*/^(),:%])/.exec(src.slice(pos));\n      if(!m) throw Error('Unsupported formula character'); tokens.push(m[0]);pos+=m[0].length;\n    }\n    let i=0,depth=0;\n    const take=t=>{if(tokens[i]!==t) throw Error('Expected '+t); i++;};\n    const cell=t=>{ const clean=t.replace(/\\$/g,''); coordinate(clean); if(stack.includes(clean)) throw Error('Circular reference at '+clean); if(stack.length>100) throw Error('Reference chain is too long'); return evaluate(ref(clean),ref,[...stack,clean]); };\n    function primary() {\n      if(++depth>60) throw Error('Formula nesting is too deep');\n      let t=tokens[i++],v;\n      if(t==='('){v=expr();take(')');}\n      else if(t && /^\\$?[A-Z]+\\$?\\d+$/.test(t)) v=cell(t);\n      else if(t && /^(\\d|\\.)/.test(t)) v=Number(t);\n      else if(['SUM','AVERAGE','MIN','MAX','EXP','LN','ABS','SQRT','ROUND'].includes(t)) {\n        take('(');const args=[];\n        if(tokens[i]!==')') do {\n          if(/^\\$?[A-Z]+\\$?\\d+$/.test(tokens[i]||'') && tokens[i+1]===':') {\n            const a=coordinate(tokens[i]),b=coordinate(tokens[i+2]);i+=3;\n            if(b[0]<a[0]||b[1]<a[1]||(b[0]-a[0]+1)*(b[1]-a[1]+1)>1000) throw Error('Invalid or oversized range');\n            for(let r=a[0];r<=b[0];r++) for(let c=a[1];c<=b[1];c++) args.push(cell(colName(c)+(r+1)));\n          } else args.push(expr());\n          if(tokens[i]!==',') break;i++;\n        } while(true);\n        take(')');\n        if(!args.length) throw Error('Function needs arguments');\n        if(['EXP','LN','ABS','SQRT'].includes(t)&&args.length!==1) throw Error(t+' needs one argument');\n        if(t==='ROUND'&&(args.length!==2||!Number.isInteger(args[1])||Math.abs(args[1])>12)) throw Error('Use ROUND(value, digits), up to 12 digits');\n        const sum=()=>args.reduce((a,b)=>a+b,0);\n        const f={SUM:sum,AVERAGE:()=>sum()/args.length,MIN:()=>Math.min(...args),MAX:()=>Math.max(...args),EXP:()=>Math.exp(args[0]),LN:()=>Math.log(args[0]),ABS:()=>Math.abs(args[0]),SQRT:()=>Math.sqrt(args[0]),ROUND:()=>Math.sign(args[0])*Math.round(Math.abs(args[0])*10**args[1])/10**args[1]};v=f[t]();\n      } else throw Error('Use a cell, number, or supported function');\n      while(tokens[i]==='%'){i++;v/=100;} depth--;return v;\n    }\n    function unary(){if(tokens[i]==='+'){i++;return unary();}if(tokens[i]==='-'){i++;return -unary();}return power();}\n    function power(){let v=primary();if(tokens[i]==='^'){i++;v=v**unary();}return v;}\n    function term(){let v=unary();while(['*','/'].includes(tokens[i])){const op=tokens[i++],b=unary();if(op==='/'&&b===0)throw Error('Cannot divide by zero');v=op==='*'?v*b:v/b;}return v;}\n    function expr(){let v=term();while(['+','-'].includes(tokens[i])){const op=tokens[i++],b=term();v=op==='+'?v+b:v-b;}return v;}\n    const result=expr(); if(i!==tokens.length) throw Error('Unexpected formula text');if(!Number.isFinite(result))throw Error('Result is not a finite number');return result;\n  }\n  function shift(formula,rows,cols=0) {\n    return String(formula).replace(/(?<![A-Z0-9_.])(\\$?)([A-Z]+)(\\$?)([1-9]\\d*)/gi,(_,ac,c,ar,r)=>{const ci=colIndex(c)+(ac?0:cols),ri=Number(r)+(ar?0:rows);if(ci<0||ri<1)throw Error('Reference would move outside the sheet');return ac+colName(ci)+ar+ri;});\n  }\n  const api={evaluate,shift,coordinate,colName}; if(typeof module!=='undefined') module.exports=api; root.SheetMath=api;\n})(typeof window!=='undefined'?window:globalThis);\n"

def worksheet_asset(name, fallback):
    try:return (ROOT/name).read_text(encoding='utf-8')
    except FileNotFoundError:return fallback


def worksheet(config):
    config=dict(config);config['id']='story-'+config['id']+'-'+hashlib.sha256(json.dumps(config,sort_keys=True).encode()).hexdigest()[:10]
    html=worksheet_asset('worksheet.html',BUNDLED_WORKSHEET).replace('/*ENGINE*/',worksheet_asset('formula.js',BUNDLED_ENGINE))
    st.iframe((html.replace('</head>',WORKSHEET_CSS+'</head>')).replace('/*CONFIG*/',json.dumps(config).replace('</','<\\/')),height='content')


def optional_practice(ch,index):
    with st.expander('Explore further · optional calculation practice'):
        st.write('This is a separate practice example. The full spreadsheet tools are here if you want to construct every step yourself; they are not required for the story.')
        factories={'forward':forward_strip,'equal':lambda:equal_swap(inputs=(F,D,[10000]*4)),
                   'unequal':lambda:unequal_swap(inputs=(F,D,[10000,10000,20000,10000])),
                   'settlement':settlements,'curve':curve_changes,'payment':single_payment,
                   'value':replacement,'risk':mismatch,'carry':lambda:carry_lesson(kind='Commodity carry'),'extrapolation':extrapolation}
        example=factories[ch['practice']]()
        if ch['practice']=='carry':
            kind=st.selectbox('Additional supporting calculation',['Commodity carry','Discount factors','Index benchmark','Implied convenience yield'])
            example=carry_lesson(kind=kind)
        if ch['practice']=='settlement':
            if st.checkbox('Practice the producer’s side instead'):example=settlements(producer=True)
        if ch['practice']=='risk':
            if st.checkbox('Practice basis mismatch instead'):example=mismatch(basis=True)
        prose(example['setting']);st.latex(example['formula']);worksheet(example['worksheet'])
        if st.checkbox('Open a blank scratchpad',key=f'free-{index}'):worksheet(scratchpad(f'story-{index}'))


st.session_state.setdefault('scene',0)
st.session_state.setdefault('revealed',{})
st.session_state.setdefault('finished',{})
st.session_state.setdefault('attempts',{})
st.session_state.setdefault('saved_answers',{})


def go(index):
    st.session_state.scene=index


index=st.session_state.scene
st.sidebar.title('Riverside Refinery')
st.sidebar.write('Commodity Swap Studio · **v2.1**')
st.sidebar.caption('One firm. One decision at a time.')
st.sidebar.progress(min(index,10)/10)
with st.sidebar.expander('Journey · jump to a chapter'):
    destination=st.selectbox('Chapter',range(11),index=index,format_func=lambda i:STORY[i]['title'] if i<10 else '11 · Advise Maya')
    st.button('Go to chapter',on_click=go,args=(destination,))
st.sidebar.write('**Core story:** chapters 1–6\n\n**Follow-up decisions:** 7–8\n\n**Input assumptions:** 9–10\n\n**Final debrief:** 11')
st.sidebar.caption('All data are hypothetical. Prices are $/barrel; quantities are barrels. Rates are continuously compounded. Ungraded; no identity or grades collected.')

if index==10:
    st.title('11 · Advise Maya')
    st.markdown('<div class="objective">Explain swap-rate behavior and price a nonstandard fixed leg without the worked steps.</div>',unsafe_allow_html=True)
    st.write('Maya wants your recommendation. Use what you learned, rather than a formula supplied with each answer. You can write a number or arithmetic expression in the calculation boxes.')
    st.subheader('First: distinguish shape from level')
    a=st.radio('Someone says: “The curve moved from contango to backwardation, so the swap rate must have fallen.”',
               ['The statement is always true','We need the actual price changes and the valuation weights'],index=None,key='final-shape')
    st.subheader('Then: price a new contract')
    prose('For this new offer, Riverside buys 10,000 barrels at each of two dates. The forwards are $70 and $80; the discount factors are 0.96 and 0.90.')
    grid(['Year','Forward ($/barrel)','D','Quantity (barrels)'],[[1,70,.96,10000],[2,80,.90,10000]])
    b=st.text_input('Fair level price ($/barrel)',key='final-rate')
    preview(b)
    c=st.text_input('One fixed payment at year 2 for both floating receipts ($)',key='final-payment')
    preview(c)
    d=st.radio('If both forwards rise by $4, with quantities and discounts unchanged, the fair level price:',
               ['Rises by exactly $4','Rises by less than $4 because of discounting','Cannot be determined'],index=None,key='final-parallel')
    if st.button('Review my recommendation',type='primary'):
        results=[a=='We need the actual price changes and the valuation weights',False,False,d=='Rises by exactly $4']
        for j,(raw,expected,tol) in enumerate([(b,139.2/1.86,.01),(c,1392000/.90,1)],1):
            try:results[j]=abs(calculate(raw)-expected)<=tol
            except (ValueError,SyntaxError,ZeroDivisionError,OverflowError):pass
        st.session_state['final_attempted']=True
        if all(results):
            st.success('You have connected the economics and the calculation: compare the actual forward changes; equate present values; and distinguish a per-barrel rate from a total fixed payment.')
        else:
            names=['Curve-shape interpretation','Level-price calculation','Single-payment calculation','Parallel-shift interpretation']
            for name,ok in zip(names,results):
                (st.success if ok else st.warning)(name+(': correct.' if ok else ': revisit this part.'))
    if st.session_state.get('final_attempted'):
        with st.expander('Review the reasoning and worked answers'):
            prose('Shape alone is insufficient. The level price is (0.96 × 70 + 0.90 × 80) / (0.96 + 0.90) = $74.8387 per barrel. The single payment is 10,000 × (0.96 × 70 + 0.90 × 80) / 0.90 = $1,546,666.67. A parallel $4 increase raises the weighted average by exactly $4.')
            st.write('Same first forward and lower later forwards → lower K. A higher overall backwardated curve can instead give a higher K. One fixed payment → match the PV of all floating-equivalent amounts, then divide by the fixed-payment discount factor.')
    with st.expander('Optional: use a free scratchpad'):worksheet(scratchpad('final'))
    st.button('Return to the refinery’s first decision',on_click=go,args=(0,))
    st.stop()

ch=STORY[index]
st.caption(f'CHAPTER {index+1} OF 10 · '+('CORE STORY' if index<6 else 'FOLLOW-UP DECISION' if index<8 else 'SHORT EXTENSION'))
st.title(ch['title'])
st.markdown('<div class="objective"><strong>You will learn to:</strong> '+ch['objective']+'</div>',unsafe_allow_html=True)
prose(ch['story'])
st.subheader('Predict before calculating')
prediction=st.radio(ch['predict'],ch['choices'],index=None,key=f'prediction-{index}')
if st.button('See what happens',type='primary',key=f'reveal-{index}'):
    if prediction is None:st.info('Make a prediction first. It is fine to be unsure—this is practice.')
    else:st.session_state.revealed[index]=True

if st.session_state.revealed.get(index):
    prose('**What matters:** '+ch['reason'])
    st.subheader('Work through Maya’s decision')
    prose(ch['worked'])
    rows=[list(row) for row in ch['rows']]
    blank_number=0
    for row in rows:
        for column,cell in enumerate(row):
            if cell=='Your turn':
                raw=st.session_state.saved_answers.get(f'answer-{index}-{blank_number}','')
                try:row[column]=calculate(raw)
                except (ValueError,SyntaxError,ZeroDivisionError,OverflowError):pass
                blank_number+=1
    # Present an authentic partial table. Only the decisive row and rate are unfinished.
    if index==1:
        raw=st.session_state.saved_answers.get('answer-1-0','')
        try:
            product=calculate(raw);rows[3][3]=product;rows[4][3]=sum(F[i]*D[i] for i in range(3))+product
        except (ValueError,SyntaxError,ZeroDivisionError,OverflowError):pass
    grid(ch['headers'],rows)
    st.latex(ch['formula'])
    st.caption('D is the given discount factor. K is the fixed price (S̄ in the course notes). A positive receipt is cash received; a negative receipt is cash paid. Intermediate calculations keep full precision.')
    st.subheader('Your turn · finish the decisive step')
    st.caption('Type a number or calculation, with or without =. Press Enter or click outside the box to see the calculated result.')
    raw_values=[]
    def save_answer(key):
        st.session_state.saved_answers[key]=st.session_state[key]
        st.session_state.finished.pop(index,None)
        st.session_state.attempts.pop(index,None)
    for n,t in enumerate(ch['tasks']):
        key=f'answer-{index}-{n}'
        raw_values.append(st.text_input(t['label'].replace('$',r'\$'),value=st.session_state.saved_answers.get(key,''),key=key,
                         help='Enter a number or a calculation, such as 64 - 72, 285.52 / 3.67, or 72 * EXP(0.03). A leading = is optional. Press Enter or click outside to calculate.',on_change=save_answer,args=(key,)))
        preview(raw_values[-1])
    if st.button('Check my thinking',type='primary',key=f'check-{index}'):
        st.session_state.attempts[index]=True
    if st.session_state.attempts.get(index):
        all_correct=True
        for raw,t in zip(raw_values,ch['tasks']):
            try:
                result=calculate(raw)
                label=t['label'].replace('$',r'\$')
                if abs(result-t['answer'])<=t['tolerance']:st.success(f'Correct — {label}: {result:,.6f}. '+t['explanation'].replace('$',r'\$'))
                else:st.warning(f'Not correct yet — {label}: your entry evaluates to {result:,.6f}. '+t['explanation'].replace('$',r'\$'));all_correct=False
            except (ValueError,SyntaxError,ZeroDivisionError,OverflowError):
                label=t['label'].replace('$',r'\$')
                st.warning(('Still blank — ' if not raw.strip() else 'Could not calculate — ')+label+'. Enter a number or arithmetic expression, with or without =.');all_correct=False
        if all_correct:st.session_state.finished[index]=True
    with st.expander('Need a nudge?'):
        for t in ch['tasks']:prose(t['explanation'])
        if st.button('Walk me through this step',key=f'walk-{index}'):
            st.session_state.finished[index]=True
            for t in ch['tasks']:prose(f"{t['label']}: {t['formula']} = {t['answer']:,.4f}")
    if st.session_state.finished.get(index):
        st.subheader('What Maya takes away')
        prose(ch['conclusion'])
        if index==4:
            st.subheader('One more thought: is the curve label enough?')
            grid(['Curve','Years 1, 2, 3, 4 ($/barrel)','Fair K ($/barrel)'],
                 [['Original contango','72, 76, 80, 84',K],['Backwardation, same first forward','72, 68, 64, 60',KB],['Backwardation, higher price level','92, 88, 84, 80','Predict first']])
            thought=st.radio('Compared with the original curve, the higher-level backwardated curve gives:',
                             ['A higher swap rate','A lower swap rate because it slopes down'],index=None,key='curve-twist')
            if st.button('Explain this comparison'):
                if thought is None:st.info('Choose a prediction first.')
                else:
                    prose(f'The higher-level backwardated curve gives K = ${KH:.4f}, above the original ${K:.4f}. The discount-weighted average of the actual prices determines the rate. “Backwardation” describes slope; it does not say where the whole curve sits.')
            studio_line_chart(pd.DataFrame({'Year':[1,2,3,4],'Original contango':F,'Anchored backwardation':BACK,'Higher backwardation':HIGH}).set_index('Year'),
                          x_label='Maturity (years)',y_label='Forward price ($/barrel)',color=['#00796b','#d05b18','#5545a2'])
        if index==5:
            st.subheader('Move the one payment earlier')
            prose('Suppose Maya pays at year 1 instead. The discount factor is 0.97. The floating leg is unchanged. Predict whether the nominal fixed payment becomes smaller or larger before opening the comparison.')
            with st.expander('Compare the two payment dates'):
                grid(['Fixed-payment date','Fixed amount ($)','Discount factor','PV ($)'],[[1,PV/.97,.97,PV],[4,PV/.86,.86,PV]])
                prose('The earlier payment is smaller in nominal dollars but due sooner. Neither is cheaper in present-value terms. The year-1 payment may require cash before the later physical purchases and floating receipts; year-4 settlement defers the fixed obligation. Equal present values do not imply equal funding or credit exposure.')
        prose('**Next in the story:** '+ch['bridge'])
    optional_practice(ch,index)

st.divider()
left,right=st.columns(2)
left.button('← Previous decision',disabled=index==0,on_click=go,args=(max(0,index-1),))
right.button('Next decision →' if index<9 else 'Advise Maya →',on_click=go,args=(index+1,),disabled=not st.session_state.finished.get(index,False))
if index==5 and st.session_state.finished.get(index):
    st.button('Finish the core session: advise Maya now',on_click=go,args=(10,))
with st.expander('Assumptions and retry'):
    st.write('Matching oil reference, dates and quantities are assumed unless explicitly relaxed. Clean valuation excludes fees and credit adjustments. Forwards are valuation inputs, not spot forecasts; futures daily margining is not modeled. Carry examples assume positive prices and proportional costs. Entries are ungraded practice, not saved assignments.')
    if st.button('Retry this chapter',key=f'retry-{index}'):
        for store in ['revealed','finished','attempts']:st.session_state[store].pop(index,None)
        for n in range(len(ch['tasks'])):
            key=f'answer-{index}-{n}';st.session_state.saved_answers.pop(key,None);st.session_state.pop(key,None)
        st.session_state.pop(f'prediction-{index}',None);st.rerun()

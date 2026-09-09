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


def worksheet(config):
    config=dict(config);config['id']='story-'+config['id']+'-'+hashlib.sha256(json.dumps(config,sort_keys=True).encode()).hexdigest()[:10]
    html=(ROOT/'worksheet.html').read_text(encoding='utf-8').replace('/*ENGINE*/',(ROOT/'formula.js').read_text(encoding='utf-8'))
    st.iframe(html.replace('/*CONFIG*/',json.dumps(config).replace('</','<\\/')),height='content')


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
            st.line_chart(pd.DataFrame({'Year':[1,2,3,4],'Original contango':F,'Anchored backwardation':BACK,'Higher backwardation':HIGH}).set_index('Year'),
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

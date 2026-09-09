"""Small calculation-first lessons. All market inputs are hypothetical.

The expected values use the financial engine/arithmetic independently of the
browser's formula evaluator. Every worksheet includes explicit symbolic steps.
"""
import math
import random
from finance import discount, fair_price, value_fixed_payer, buyer_cost, carry, implied_yield


def calc(expected, formula, process, hint='', tolerance=None):
    result = dict(value='', locked=False, expected=float(expected), formula=formula,
                  process=process, hint=hint or process)
    if tolerance is not None:
        result['tolerance'] = tolerance
    return result


def sheet(key, title, headers, rows, guides, interpretation, instructions='Work from top to bottom. Select a yellow cell for a hint, or select any cell in a row to check that row.'):
    cells = {}
    for r, row in enumerate(rows, 1):
        assert len(row) == len(headers)
        for c, value in enumerate(row):
            cells[f'{chr(65+c)}{r}'] = value if isinstance(value, dict) else dict(value=value, locked=True, text=isinstance(value,str))
    return dict(id=key, title=title, headers=headers, rows=len(rows), cells=cells,
                rowGuides=guides, interpretation=interpretation, instructions=instructions)


def lesson(title, objective, setting, formula, notation, steps, worksheet, question, choices, answer, explanation, limitation):
    return dict(title=title, objective=objective, setting=setting, formula=formula, notation=notation,
                steps=steps, worksheet=worksheet, question=question, choices=choices, answer=answer,
                explanation=explanation, limitation=limitation)


def market(seed=0):
    if seed == 0:
        return [72.,75.,74.,78.5], [.97,.94,.90,.86], [10000.,15000.,20000.,10000.]
    rng=random.Random(seed)
    return [float(rng.randrange(60,91)) for _ in range(4)], [.98,.95,.92,.88], [float(rng.choice([5000,10000,15000,20000])) for _ in range(4)]


def equal_swap(seed=0, inputs=None):
    f,d,_=market(seed) if inputs is None else inputs
    k=fair_price(f,d); products=[a*b for a,b in zip(f,d)]
    rows=[[i+1,f[i],d[i],calc(products[i],f'=B{i+1}*C{i+1}','multiply this forward by its discount factor','Use the two given cells in this row.')] for i in range(4)]
    rows += [['Totals','',calc(sum(d),'=SUM(C1:C4)','add all four discount factors'),calc(sum(products),'=SUM(D1:D4)','add all four products')],['Fair K ($/unit)','','',calc(k,'=D5/C5','divide the product total by the discount-factor total','The denominator is not the number of dates.',.005)]]
    ws=sheet(f'equal-{seed}', 'Four columns: build the fair fixed price', ['Date (years)','Forward F ($/unit)','Discount factor D','Product D × F'],rows,
             ['Step 1: calculate this dated product.']*4+['Step 2: sum columns C and D separately.','Step 3: divide D5 by C5.'],
             'The fixed price lies within the forward-price range. Equal quantities cancel; the discount factors generally do not.')
    return lesson('Price a swap with equal quantities','Compute the fair fixed price from four forwards and four discount factors.',
        'A manufacturer buys the same quantity in years 1–4. It wants one fixed price per unit instead of four different forward prices. Each floating payment uses the same commodity reference as the physical purchase.',
        r'K\sum_j D_j=\sum_jD_jF_j\quad\Longrightarrow\quad K=\frac{\sum_jD_jF_j}{\sum_jD_j}',
        'F is a dated forward price ($/unit); D is the given date-0 discount factor (no units); K is the fair fixed price ($/unit). In the course notes, K is written as S-bar and D as P(0,t). Equal quantity Q cancels from both sides.',
        ['Multiply each forward price by its discount factor.','Sum the products and, separately, the discount factors.','Divide the product sum by the discount-factor sum.','Check that K is between the lowest and highest forward prices.'],ws,
        'Why do we divide by the sum of discount factors?', ['Because the fixed price is paid at all four dates and each payment must be discounted','Because there are four prices','Because the last forward is most important'],0,
        'The fixed leg has present value QKΣD. Equating it to QΣDF makes the inception swap value zero. A simple average works when discount factors are also equal.',
        'Matching dates and quantities; no fees or credit adjustments. A fair fixed price is not a forecast and is not the swap’s dollar value.')


def unequal_swap(seed=0, inputs=None):
    f,d,q=market(seed) if inputs is None else inputs;k=fair_price(f,d,q)
    dq=[a*b for a,b in zip(d,q)];dqf=[a*b for a,b in zip(dq,f)]
    rows=[[i+1,f[i],d[i],q[i],calc(dq[i],f'=C{i+1}*D{i+1}','multiply discount factor by quantity'),calc(dqf[i],f'=B{i+1}*E{i+1}','multiply the forward by discounted quantity')] for i in range(4)]
    rows += [['Totals','','','',calc(sum(dq),'=SUM(E1:E4)','sum discounted quantities'),calc(sum(dqf),'=SUM(F1:F4)','sum discounted forward commitments')],['Fair K ($/unit)','','','','',calc(k,'=F5/E5','divide total discounted commitments by total discounted quantities',tolerance=.005)]]
    ws=sheet(f'unequal-{seed}','One modification: include quantity',['Date (years)','F ($/unit)','D','Q (units)','D × Q','D × Q × F ($)'],rows,
        ['First E: discounted quantity. Then F: its forward commitment.']*4+['Sum E and F separately.','Divide F5 by E5.'],
        'A larger purchase gives its dated forward more influence. Equal quantities reproduce the four-column method.')
    return lesson('Price a swap with unequal quantities','Modify the equal-quantity process to allow seasonal purchases.',
        'A utility buys different amounts at each annual date. One unit purchased in a high-volume year cannot be given the same total influence as all units purchased in a low-volume year.',
        r'K=\frac{\sum_jD_jQ_jF_j}{\sum_jD_jQ_j}',
        'Q is units purchased and hedged at that date. DQ is discounted quantity. DQF is the present value of the dated forward-price commitment in dollars.',
        ['Calculate D × Q for each date.','Multiply each discounted quantity by its forward price.','Sum both calculated columns.','Divide total DQF by total DQ.'],ws,
        'If every quantity doubles, with forwards and discount factors unchanged, what happens to K?', ['K doubles','K is unchanged','K halves'],1,
        'Both numerator and denominator double, leaving the per-unit fixed price unchanged. Total dollar commitments double.',
        'These are contracted quantities. Realized purchases may differ; that creates quantity risk, explored later.')


def forward_strip(seed=0):
    f,d,q=market(seed);q=[10000.]*4;s=[x+v for x,v in zip(f,[8,-7,11,-5])]
    rows=[]
    for i,(fi,si) in enumerate(zip(f,s),1):
        rows.append([i,si,fi,calc(si-fi,f'=B{i}-C{i}','calculate the long-forward receipt S − F'),calc(fi,f'=B{i}-D{i}','subtract the forward receipt from physical purchase cost per unit')])
    ws=sheet(f'strip-{seed}','First cancel the uncertainty, one date at a time',['Year','Physical S ($/unit)','Forward F ($/unit)','Receipt S − F','Effective cost'],rows,
        ['Compute the forward receipt; then subtract it from the physical price.']*4,
        'Each effective purchase price equals its own forward price. A strip locks several dated prices; it does not yet create a single common price.')
    return lesson('From physical purchases to a forward strip','Choose the buyer’s hedge direction and verify cash-flow cancellation.',
        'A manufacturer must buy 10,000 units at each of four annual dates. Higher spot prices raise its cost. It takes a long forward on 10,000 units at each date. Begin with one unit; multiply by 10,000 for dollar totals.',
        r'\text{Long-forward receipt}=S_j-F_j,\qquad \text{effective cost}=S_j-(S_j-F_j)=F_j',
        'S is the realized physical price; F is the contracted forward price, both $/unit. A positive receipt is money received; a negative receipt is money paid. Physical purchase cost is shown as a positive expense.',
        ['Identify the exposure: the buyer is hurt by rising prices.','Use a long forward, which receives S − F at maturity.','Calculate that receipt for each date.','Subtract the receipt from the physical price.'],ws,
        'A forward has a negative settlement when the commodity becomes cheaper. Has the hedge necessarily failed?', ['Yes','No: the cheaper purchase offsets the forward payment'],1,
        'Evaluate the combined purchase and hedge. The loss on the forward is offset by a lower physical purchase price.',
        'This cancellation assumes identical reference prices, dates and quantities. Futures daily marking-to-market is not modeled.')


def settlements(seed=0, producer=False):
    f,_,_=market(seed);k=75. if seed==0 else f[0];s=[k+7,k-8,k+10,k-2];rows=[]
    for i,si in enumerate(s,1):
        receipt=k-si if producer else si-k
        rows.append([i,si,k,calc(receipt,f'=C{i}-B{i}' if producer else f'=B{i}-C{i}','subtract S from K' if producer else 'subtract K from S'),calc(k,f'=B{i}+D{i}' if producer else f'=B{i}-D{i}','add the receipt to sales revenue' if producer else 'subtract the receipt from purchase cost')])
    ws=sheet(f'settle-{producer}-{seed}','Settle one unit first',['Year','Physical S ($/unit)','Fixed K ($/unit)','Swap receipt ($/unit)','Effective '+('revenue' if producer else 'cost')],rows,['Calculate D, then combine the physical transaction and swap in E.']*4,
             'Every row ends at K. Negative swap receipts are payments; they do not by themselves indicate hedge failure.')
    role='producer' if producer else 'buyer'
    return lesson('Settle the '+role+'’s swap','Compute signed swap settlements and the combined physical result.',
        f'A commodity {role} has already contracted at the given fixed price K on 10,000 units per year. K stays fixed as realized prices change. '+('The producer receives fixed and pays floating to protect sales revenue.' if producer else 'The buyer pays fixed and receives floating to protect purchase costs.'),
        r'\text{Receipt}=K-S,\quad\text{revenue}=S+(K-S)=K' if producer else r'\text{Receipt}=S-K,\quad\text{cost}=S-(S-K)=K',
        'All worksheet entries are $/unit. To scale: total swap receipt = Q × per-unit receipt; total effective cost or revenue = QK. With Q = 10,000, multiply by 10 to express totals in $000.',
        ['Identify who pays fixed and who receives fixed.','Calculate the signed per-unit swap receipt.','Combine that receipt with physical cost or revenue.','Use the scaling worksheet below to convert per-unit receipts into dollar totals.'],ws,
        'Does the fixed price change when realized spot changes?', ['Yes, to match spot','No, it was set in the contract'],1,
        'The contract price remains fixed. The realized settlement adjusts, offsetting the physical-price movement.',
        'A swap stabilizes the matched effective price. It also gives up the benefit of favorable physical-price moves on those hedged units.')


def scaling(seed=0, producer=False):
    f,_,_=market(seed);k=75. if seed==0 else f[0];s=k+7;receipt=k-s if producer else s-k
    return sheet(f'scale-{producer}-{seed}','Then scale the first settlement',['Input or calculation','Value'],
        [['Quantity (units)',10000],['Physical S ($/unit)',s],['Fixed K ($/unit)',k],['Receipt ($/unit)',calc(receipt,'=B3-B2' if producer else '=B2-B3','calculate the signed per-unit receipt')],
         ['Physical total ($)',calc(10000*s,'=B1*B2','multiply quantity by physical price')],['Swap total ($)',calc(10000*receipt,'=B1*B4','multiply quantity by signed per-unit receipt')],
         ['Net total ($)',calc(10000*k,'=B5+B6' if producer else '=B5-B6','add receipt to revenue' if producer else 'subtract receipt from physical cost')]],
        ['Given input.']*3+['Calculate the receipt.','Scale physical dollars.','Scale swap dollars.','Combine the physical and swap dollar amounts.'],'Net dollars equal QK. Total cash flow is different from the per-unit price.')


def curve_changes(seed=0, scenario='Parallel increase'):
    f,d,_=market(seed)
    changed={'Parallel increase':[x+5 for x in f], 'Parallel decrease':[x-5 for x in f], 'Contango':[f[0]+5*i for i in range(4)],'Backwardation':[f[0]-5*i for i in range(4)],'Late scarcity':[f[i]+(12 if i==3 else 0) for i in range(4)]}[scenario]
    old=fair_price(f,d);new=fair_price(changed,d);rows=[]
    for i in range(4):
        n=i+1;rows.append([n,f[i],changed[i],d[i],calc(d[i]*f[i],f'=B{n}*D{n}','discount the old forward'),calc(d[i]*changed[i],f'=C{n}*D{n}','discount the scenario forward')])
    rows += [['Totals','','',calc(sum(d),'=SUM(D1:D4)','sum discount factors'),calc(sum(a*b for a,b in zip(f,d)),'=SUM(E1:E4)','sum old products'),calc(sum(a*b for a,b in zip(changed,d)),'=SUM(F1:F4)','sum scenario products')],['K ($/unit)','','','',calc(old,'=E5/D5','divide old total by sum D',tolerance=.005),calc(new,'=F5/D5','divide scenario total by sum D',tolerance=.005)],['Change in K','','','','',calc(new-old,'=F6-E6','subtract the old rate from the new rate',tolerance=.005)]]
    ws=sheet(f'curve-{scenario}-{seed}','Reprice the same purchases under a new curve',['Year','Old F','Scenario F','D','Old D × F','New D × F'],rows,['Calculate both products using the same discount factor.']*4+['Sum D and each product column.','Compute both fair rates.','Subtract old K from new K.'],
        'A parallel $5 increase raises K by $5. A change at just one maturity has a smaller effect because only part of the discounted purchases is affected.')
    return lesson('How curve changes affect a new swap quote','Recompute a fair swap rate and identify the source of its change.',
        'A procurement manager compares today’s quote with a hypothetical alternative curve for the same equal annual quantities. This prices a new swap; it does not reset an existing contract’s K.',
        r'K_{new}-K_{old}=\frac{\sum_jD_j(F_{new,j}-F_{old,j})}{\sum_jD_j}',
        'Old F and scenario F are $/unit. Discount factors and quantities are held fixed. Contango means rising forwards across maturity; backwardation means falling forwards.',
        ['Compare the two forward columns and predict the direction of change.','Compute discounted products for both curves.','Use the same denominator to price both swaps.','Subtract old K from new K and explain which dates drove the change.'],ws,
        'Does contango prove that future spot prices will rise?', ['Yes','No: curve shape is not a physical-price forecast'],1,
        'Curve shape reflects carry and market conditions. It does not establish the direction of future realized spot prices.',
        'Scenarios are hypothetical. This exercise holds rates and quantities fixed to isolate the forward-price effect.')


def single_payment(seed=0, payment_year=4):
    f,d,_=market(seed);q=10000;pv=sum(fi*di*q for fi,di in zip(f,d));dp=d[payment_year-1];rows=[]
    for i in range(4):
        n=i+1;rows.append([n,f[i],d[i],q,calc(q*f[i]*d[i],f'=B{n}*C{n}*D{n}','multiply F × D × Q to get dated present value')])
    rows += [['Total PV','','','',calc(pv,'=SUM(E1:E4)','sum all dated present values')],['Payment year',payment_year,dp,'',calc(pv/dp,'=E5/C6','divide total PV by the chosen payment-date discount factor')],['PV check','','','',calc(pv,'=E6*C6','discount the single payment back to today')]]
    ws=sheet(f'payment-{payment_year}-{seed}','Compress four fixed payments into one',['Year / step','F or year','D','Q (units)','Calculated dollars'],rows,['Calculate the date-0 value of this forward-equivalent commitment.']*4+['Sum the present values.','Calculate the nominal single fixed payment.','Verify that its PV equals E5.'],
        'The nominal payment changes with timing, but its present value equals the original strip’s present value.')
    return lesson('Move the fixed leg into a single payment','Find one payment with the same present value as the dated fixed commitments.',
        f'A buyer keeps dated floating receipts but negotiates one fixed payment at year {payment_year}. It still receives floating on 10,000 units at each annual date. How large should that single fixed payment be?',
        r'PV=\sum_jD_jQ_jF_j,\qquad X_\tau=\frac{PV}{D_\tau},\qquad D_\tau X_\tau=PV',
        'X is a total dollar payment, not a price per unit. τ is its payment date; Dτ is given in row 6. The forward amounts are valuation equivalents, not known future floating receipts.',
        ['Discount each forward-equivalent commitment.','Sum the dated present values.','Divide by the discount factor at the selected payment date.','Discount your answer back as an independent check.'],ws,
        'Do equal present values imply equal funding needs?', ['Yes','No: payment timing changes when cash is needed'],1,
        'An early fixed payment may require funding before floating receipts arrive. Deferring payment changes credit exposure. Equal inception PV does not remove these differences.',
        'Smaller discount factors imply larger nominal payments for the same PV. A later date has a smaller factor only when the relevant forward interest rate is positive.')


def replacement(seed=0):
    f=[78.,80.5,83.] if seed==0 else market(seed)[0][:3];t=[.5,1.,1.5];r=[.032,.035,.038];d=[discount(a,b) for a,b in zip(t,r)];q=180000;k=76.5
    rows=[]
    for i in range(3):
        n=i+1;rows.append([t[i],f[i],d[i],q,calc(f[i]-k,f'=B{n}-$B$5','subtract the old fixed price from current forward'),calc(q*d[i]*(f[i]-k),f'=C{n}*D{n}*E{n}','multiply the forward advantage by quantity and discount factor')])
    rows += [['Value ($)','','','','',calc(value_fixed_payer(f,d,[q]*3,k),'=SUM(F1:F3)','sum the discounted remaining advantages',tolerance=1.)],['Old K ($/unit)',k,'','','','']]
    ws=sheet(f'value-{seed}','Value a contract after the market changes',['Years remaining','Current F ($/unit)','Current D','Q (barrels)','F − old K','PV advantage ($)'],rows,['Calculate the price advantage, then its discounted dollar value.']*3+['Sum remaining values. A positive number is an asset to the fixed payer.','Given: the old contractual fixed price does not reset.'],
        'Current value is the discounted benefit of the old terms relative to current forward prices. The other party has the opposite value.')
    return lesson('Value an existing swap','Distinguish a contracted fixed price from the swap’s current dollar value.',
        'A refinery pays $76.50 per barrel on 180,000 barrels at each remaining date. Current forward prices have changed. Calculate the value today to the fixed payer, immediately after any previous settlement.',
        r'V_{payer}=\sum_jD_jQ_j(F_{current,j}-K_{old}),\qquad V_{receiver}=-V_{payer}',
        'Times run from the valuation date to remaining payments. F and K are $/barrel, Q is barrels, V is dollars. Row 5 contains the old K.',
        ['Keep the old fixed price unchanged.','Subtract it from each current forward.','Multiply each difference by quantity and current discount factor.','Sum the remaining values and interpret the sign.'],ws,
        'If the current replacement fixed price exceeds old K, the old swap is what to its fixed payer?', ['An asset','A liability','Always zero'],0,
        'Paying below the current market price is valuable. At inception, a fairly priced swap has zero value; that need not remain true.',
        'This is a clean value excluding collateral, credit adjustments, bid–ask costs and accrued unsettled amounts.')


def mismatch(seed=0, basis=False):
    k=75.;index=82. if seed==0 else float(market(seed)[0][0]);actual=10000.;hedged=10000. if basis else 15000.;physical=index+3 if basis else index
    cost=buyer_cost(physical,index,k,actual,hedged)
    rows=[['Physical price',physical],['Index price',index],['Fixed price',k],['Actual units',actual],['Swap units',hedged],['Physical cost ($)',calc(actual*physical,'=B1*B4','multiply actual quantity by actual physical price')],['Swap receipt ($)',calc(hedged*(index-k),'=B5*(B2-B3)','multiply swap quantity by index minus fixed price')],['Net cost ($)',calc(cost,'=B6-B7','subtract signed swap receipt from physical cost')],['Cost / actual unit',calc(cost/actual,'=B8/B4','divide net cost by actual quantity',tolerance=.005)]]
    ws=sheet(f'risk-{basis}-{seed}','Audit what the hedge actually covers',['Input or calculation','Value'],rows,
        ['Given input; prices are $/unit and quantities are units.']*5+['Compute physical dollars.','Compute derivative dollars with the contracted quantity and reference index.','Combine the two dollar amounts.','Divide by actual physical units.'],
        'With matching quantities but a $3 basis, effective cost is K + $3.' if basis else 'An excess swap position retains price exposure. Above K it gains; below K it loses. A favorable result in one state does not remove risk.')
    return lesson('Residual '+('basis' if basis else 'quantity')+' risk','Compute effective cost when the physical exposure and swap do not match.',
        'A buyer hedges its purchase. '+('The quantity matches, but the purchased commodity costs $3 more per unit than the swap index.' if basis else 'A warm winter reduces actual purchases below the contracted hedge quantity.'),
        r'C=Q_{actual}S_{physical}-Q_{swap}(S_{index}-K),\qquad c=C/Q_{actual}',
        'C is net dollar cost; c is dollars per actual purchased unit. A swap settles on its own quantity and reference price, not automatically on the firm’s actual expenditure.',
        ['Separate the physical price and quantity from the swap index and quantity.','Calculate physical dollars and swap dollars separately.','Subtract the swap receipt from physical cost.','Divide by actual units; compare the result with K.'],ws,
        'Does a favorable net outcome prove that the hedge has eliminated risk?', ['Yes','No: a mismatch can help in one state and hurt in another'],1,
        'Hedge quality concerns how exposure changes across outcomes, not whether one realized outcome happens to be favorable.',
        'Quantity, basis, funding and counterparty risk can remain. This worksheet isolates one mismatch at a time.')


def carry_lesson(seed=0, kind='Discount factors'):
    t=[1.,2.,3.,4.];r=[.032,.0355,.0385,.041];spot=70. if seed==0 else market(seed)[0][0];storage=.015;y=.025;div=.015
    if seed:
        rng=random.Random(seed)
        r=[v+rng.choice([-.005,.0025,.0075]) for v in r]
    index_spot=100. if seed==0 else float(90+seed%23)
    if kind=='Discount factors':
        rows=[[a,b,calc(discount(a,b),f'=EXP(-A{i}*B{i})','multiply −r × t, then apply EXP','EXP(x) means e raised to x. Rates are decimals.')] for i,(a,b) in enumerate(zip(t,r),1)]
        form=r'D(0,t)=e^{-r(t)t}';headers=['t (years)','r (decimal / year)','D (no units)'];objective='Calculate a discount factor using a continuously compounded zero rate.';meaning='D is today’s value of $1 received at the date.';steps=['Read the time in years and rate in decimal form.','Multiply the rate by time and change the sign.','Apply EXP to get the discount factor.','Check that positive rates produce D between zero and one.']
    elif kind=='Index benchmark':
        rows=[[a,b,index_spot,div,calc(index_spot*math.exp((b-div)*a),f'=C{i}*EXP((B{i}-D{i})*A{i})','subtract dividend yield from financing rate, multiply by time, then exponentiate and multiply by spot')] for i,(a,b) in enumerate(zip(t,r),1)]
        form=r'F(0,t)=S_0e^{(r(t)-q)t}';headers=['t (years)','r (decimal)','Index spot','Dividend q','Forward index'];objective='Build an index forward price from financing cost and dividend yield.';meaning='q is the continuous proportional dividend yield. Index prices are index points.';steps=['Start from the spot index.','Subtract dividend yield from the financing rate.','Multiply net carry by time and apply EXP.','Multiply by spot. Compare F with spot.']
    elif kind=='Commodity carry':
        rows=[[a,b,spot,storage,y,calc(carry(spot,b,storage,y,a),f'=C{i}*EXP((B{i}+D{i}-E{i})*A{i})','calculate r + storage − convenience yield, multiply by time, exponentiate and multiply by spot')] for i,(a,b) in enumerate(zip(t,r),1)]
        form=r'F(0,t)=S_0e^{(r(t)+u-y)t}';headers=['t (years)','r (decimal)','Spot ($/unit)','Storage u','Convenience y','F ($/unit)'];objective='Construct commodity forwards using a proportional cost-of-carry model.';meaning='u is annual storage cost as a fraction of price; y is the annual convenience benefit of holding inventory. Both are decimal rates.';steps=['Add financing and proportional storage costs.','Subtract the convenience benefit.','Multiply net carry by time; apply EXP.','Multiply by spot to obtain the forward price.']
    else:
        f=market(seed)[0];rows=[[a,b,spot,storage,f[i-1],calc(implied_yield(spot,f[i-1],b,storage,a),f'=B{i}+D{i}-LN(E{i}/C{i})/A{i}','compute LN(F / spot) divided by time, then subtract it from r + storage')] for i,(a,b) in enumerate(zip(t,r),1)]
        form=r'\bar y(0,t)=r(t)+u-\frac{\ln(F(0,t)/S_0)}{t}';headers=['t (years)','r (decimal)','Spot ($/unit)','Storage u','Given F ($/unit)','Implied y (decimal)'];objective='Infer average convenience yield from a forward price under the carry model.';meaning='The result is a model-implied average yield from today to t. A decimal result of 0.025 means 2.5% per year.';steps=['Divide each forward by spot.','Take LN of that ratio and divide by maturity.','Subtract the result from financing plus storage.','Interpret the result as a model-implied average, conditional on the inputs.']
    ws=sheet(f'carry-{kind}-{seed}',kind+' worksheet',headers,rows,['Use the stated formula for this maturity.']*4,meaning)
    return lesson(kind+' · supporting calculation',objective,'This supporting workshop supplies the building blocks used in swap valuation. Work through one row, then fill the formula down to the other maturities.',form,
        meaning+' All interest rates use continuous compounding; times are years.',steps,ws,
        'Does a model-implied forward price necessarily forecast realized future spot?', ['Yes','No'],1,
        'A carry relationship is a pricing relationship under assumptions; it is not a statement about physical expected spot.',
        'The index benchmark equates forwards and futures under deterministic rates. Commodity carry is a stylized positive-price inventory model; proportional storage and convenience yield are assumed. Negative commodity prices require a different model.')


def extrapolation(seed=0, y=.025):
    f,d,_=market(seed);last=f[-1];r=.045;u=.015;extension=[last*math.exp((r+u-y)*j) for j in (1,2)];extended=f+extension;ds=d+[.82,.78];k=fair_price(extended,ds)
    rows=[[i+1, f[i], d[i],calc(f[i]*d[i],f'=B{i+1}*C{i+1}','multiply the supplied forward by its discount factor')] for i in range(4)]
    rows += [[5,calc(extension[0],f'=B4*EXP(({r}+{u}-{y})*(A5-A4))','extend the last supplied forward for one year using the given net forward carry'),ds[4],calc(extension[0]*ds[4],'=B5*C5','discount the extrapolated year-5 forward')],[6,calc(extension[1],f'=B4*EXP(({r}+{u}-{y})*(A6-A4))','extend the last supplied forward for two years using the given net forward carry'),ds[5],calc(extension[1]*ds[5],'=B6*C6','discount the extrapolated year-6 forward')],['Totals','',calc(sum(ds),'=SUM(C1:C6)','sum all six discount factors'),calc(sum(a*b for a,b in zip(extended,ds)),'=SUM(D1:D6)','sum all six products')],['Six-date K','','',calc(k,'=D7/C7','divide total products by total discounts',tolerance=.005)]]
    ws=sheet(f'extrapolate-{seed}-{y}','Separate supplied inputs from modeled extensions',['Year / step','F ($/unit)','D','D × F'],rows,
        ['Years 1–4: supplied hypothetical forward inputs.']*4+['Year 5: extrapolate B5, then calculate D5.','Year 6: extrapolate B6, then calculate D6.','Sum all six dates.','Compute the level price for equal quantities.'],
        'Years 5 and 6 are model outputs, not observed quotes. Increasing assumed convenience yield lowers the extrapolated forwards and hence the six-date fixed price.')
    return lesson('Extrapolate beyond the supplied forward curve','Build two assumed long-dated forwards, then price a six-date swap.',
        'A buyer needs six annual hedges but has supplied forwards only through year four. Use an explicitly assumed incremental carry rate beyond year four. Quantities are equal. The final two discount factors are also hypothetical supplied valuation inputs.',
        r'F(0,T)=F(0,4)e^{(r_{4,T}+u-y)(T-4)},\qquad K_6=\frac{\sum_{j=1}^6D_jF_j}{\sum_{j=1}^6D_j}',
        f'Given annual carry assumptions for years 4–6: forward financing rate r = {r} (4.5%), storage u = {u} (1.5%), and incremental convenience yield y = {y} ({100*y:g}%). Use these decimal inputs in EXP. This scenario does not treat the last average implied yield as an observed future yield.',
        ['Keep the first four forward prices as supplied.','Extend from year four using the assumed net carry and the extra time.','Discount all six forward prices.','Sum products and discount factors; calculate K.','Repeat under a different convenience-yield assumption and compare your answers.'],ws,
        'Which part of the resulting quote most directly introduces extrapolation risk?', ['The two modeled forward prices beyond year four','The fact that quantities are equal'],0,
        'The long-dated portion depends on chosen assumptions. A precise calculated rate is not evidence of an observable market quote.',
        'This extension intentionally separates supplied prices from model assumptions. Alternative carry assumptions give different quotes; neither is a unique observed answer.')


BUILDERS={'Forward strip':forward_strip,'Equal quantities':equal_swap,'Unequal quantities':unequal_swap,'Buyer settlement':settlements,
          'Curve changes':curve_changes,'Single fixed payment':single_payment,'Existing swap value':replacement,'Quantity mismatch':mismatch}


def scratchpad(key):
    return sheet('scratch-'+key,'Free scratchpad',['A','B','C','D','E','F'],[[dict(value='',locked=False) for _ in range(6)] for _ in range(6)],
                 ['Free work: use numbers, references and supported spreadsheet functions.']*6,'',
                 'Use this open sheet for alternative calculations. It is separate from the guided worksheet; references refer only to cells in this sheet.')

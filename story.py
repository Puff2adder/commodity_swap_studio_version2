"""One continuing hypothetical refinery story; independent numerical answers."""
import math
from finance import fair_price, value_fixed_payer, buyer_cost, carry, implied_yield

F=[72.,76.,80.,84.]
D=[.97,.94,.90,.86]
Q=[10000.]*4
K=fair_price(F,D)
PV=sum(f*d*q for f,d,q in zip(F,D,Q))
BACK=[72.,68.,64.,60.]
KB=fair_price(BACK,D)
HIGH=[92.,88.,84.,80.]
KH=fair_price(HIGH,D)


def task(label,answer,formula,explanation,tolerance=.01):
    return dict(label=label,answer=answer,formula=formula,explanation=explanation,tolerance=tolerance)


def chapter(title,objective,story,predict,choices,correct,reason,worked,headers,rows,formula,tasks,conclusion,bridge,practice):
    return dict(title=title,objective=objective,story=story,predict=predict,choices=choices,correct=correct,reason=reason,worked=worked,
                headers=headers,rows=rows,formula=formula,tasks=tasks,conclusion=conclusion,bridge=bridge,practice=practice)


def chapters():
    sums=sum(f*d for f,d in zip(F,D)); sd=sum(D)
    quantities=[10000,10000,20000,10000];kq=fair_price(F,D,quantities)
    new=[f+5 for f in F];value=value_fixed_payer(new,D,Q,K)
    r=.04;u=.015;y=.025;forward=carry(72,r,u,y,1)
    ex=[84*math.exp(.03*i) for i in (1,2)]; ds=D+[.82,.78];six=fair_price(F+ex,ds)
    return [
      chapter('1 · Protect one purchase','Explain how a forward fixes the effective purchase price, even when its settlement is negative.',
       'Riverside Refinery must buy 10,000 barrels of oil next year. Its manager, Maya, can lock in a forward price of $72 per barrel. She worries about a price increase—but asks what happens if oil becomes cheaper.',
       'What should a successful price hedge do?', ['Keep the effective purchase price at $72 in either outcome','Make money on the forward in every outcome'],0,
       'The target is a stable combined purchase price, not a positive derivative settlement in every state.',
       'Start with the expensive-oil row. Riverside pays $80 for a barrel and receives $8 on its long forward. Its effective cost is $72. Now finish just the cheaper-oil row.',
       ['Outcome','Physical price ($/barrel)','Forward receipt ($/barrel)','Effective cost ($/barrel)'],
       [['Oil becomes expensive',80,8,72],['Oil becomes cheaper',64,'Your turn','Your turn']],
       r'\text{Receipt}=S-F,\qquad\text{effective cost}=S-(S-F)=F',
       [task('Receipt when oil is $64 ($/barrel)',-8,'64 - 72','A negative receipt is an $8 payment.'),task('Effective cost in that outcome ($/barrel)',72,'64 - (-8)','The cheaper oil and the forward payment combine to $72.')],
       'Maya accepts the forward because it removes price uncertainty on the matched purchase. If oil becomes cheaper, the refinery pays on the forward and still ends at $72. It gives up favorable price movements as well as protection against adverse ones.',
       'One forward fixes one date. Riverside now wants the same protection for four annual purchases.','forward'),
      chapter('2 · Turn four prices into one','Calculate a level fixed swap price by equating the present values of two sets of commitments.',
       'Riverside needs 10,000 barrels in each of years 1–4. Four forwards would fix prices at $72, $76, $80 and $84. Maya asks the dealer for one price K per barrel at every date.',
       'Should the dealer simply quote the arithmetic average of $78?', ['Not generally: earlier and later payments have different present values','Yes: equal quantities always imply equal weights'],0,
       'Equal quantities cancel. Discount factors still weight the dated prices. Here the lower, earlier prices receive greater weight, so K is slightly below $78.',
       'The first three products are done. In year 1, 72 × 0.97 = 69.84. Finish the last product, then divide the product-column sum by the discount-factor sum. The table totals update from your entry.',
       ['Year','Forward F ($/barrel)','Discount factor D','Product D × F'],
       [[1,72,.97,69.84],[2,76,.94,71.44],[3,80,.90,72],[4,84,.86,'Your turn'],['Total','','3.67','From your product']],
       r'QK\sum D_j=Q\sum D_jF_j\quad\Rightarrow\quad K=\frac{\sum D_jF_j}{\sum D_j}',
       [task('Year-4 product: 84 × 0.86',72.24,'84 * 0.86','This is the discounted price contribution, not a swap settlement.'),task('Fair fixed swap price K ($/barrel)',K,f'{sums:.2f} / {sd:.2f}','Divide the sum of products by the sum of discount factors. Check that the result lies between $72 and $84.')],
       f'The fair fixed price is ${K:.4f} per barrel. It preserves the present value of the forward strip. Riverside will pay the same per-barrel fixed price at all four dates, and the new swap has zero inception value under our assumptions.',
       'Maya has a base quote. The operations team now revises the purchase schedule.','equal'),
      chapter('3 · Buy more in one year','Explain and calculate how purchase quantities change the influence of each forward price.',
       'An expansion means Riverside now needs 20,000 barrels in year 3, while the other years remain at 10,000. The forward prices and discount factors have not changed.',
       'Will the revised fair fixed price rise or fall?', ['Rise: more weight moves to the $80 year','Fall: a bigger purchase always earns a lower fair price','Remain unchanged: only forward prices matter'],0,
       f'The extra barrels are priced at $80, above the old fair rate of ${K:.4f}. Giving them more weight raises the fair rate. This is valuation, not a volume-discount negotiation.',
       'Most of the table is complete. Year 3 now has discounted quantity 0.90 × 20,000 = 18,000. Its present-value commitment is 18,000 × $80 = $1,440,000. Use the two supplied sums to finish the quote.',
       ['Year','F ($/barrel)','D','Q (barrels)','D × Q','D × Q × F ($)'],
       [[i+1,F[i],D[i],quantities[i],D[i]*quantities[i],D[i]*quantities[i]*F[i]] for i in range(4)]+[['Total','','','',sum(d*q for d,q in zip(D,quantities)),sum(d*q*f for d,q,f in zip(D,quantities,F))]],
       r'K=\frac{\sum D_jQ_jF_j}{\sum D_jQ_j}',
       [task('Revised fixed price ($/barrel)',kq,'3575200 / 45700','Weight by both quantity and discount factor; the numerator and denominator have both changed.')],
       f'The revised rate is ${kq:.4f}. Doubling every purchase would leave the rate unchanged; increasing only the above-average-price year raises it. Total dollar commitments and the price per barrel are different concepts.',
       'The expansion is postponed. Riverside signs the original equal-quantity swap. We now follow that contract into settlement.','unequal'),
      chapter('4 · A payment is not a failed hedge','Judge the hedge by the physical purchase and swap together.',
       f'Riverside signs the original four-date swap at K = ${K:.4f} per barrel, paying fixed and receiving the oil index on 10,000 barrels annually. At the first settlement, oil is only $65. Maya sees a swap payment on the statement.',
       'Has the negative swap receipt shown that the hedge failed?', ['No: the physical purchase also became cheaper','Yes: a hedge should never require a payment'],0,
       'The derivative must be evaluated together with the physical purchase. A fixed-price hedge exchanges uncertainty for certainty; it does not promise free protection.',
       f'The swap receipt per barrel is 65 − {K:.4f} = {65-K:.4f}. That negative receipt means Riverside pays on the swap. The physical purchase costs $650,000. Finish the combined dollar cost.',
       ['Physical purchase ($)','Swap receipt (+) / payment (−) ($)','Combined cost ($)'],
       [[650000,10000*(65-K),'Your turn']],
       r'\text{Cost}=QS-Q(S-K)=QK',
       [task('Combined cost for 10,000 barrels ($)',10000*K,f'650000 - ({10000*(65-K):.6f})','Subtract a negative receipt: the swap payment is added to the physical expense.',1)],
       f'The net cost is ${10000*K:,.2f}, or ${K:.4f} per barrel, as contracted. A producer would take the opposite swap direction: receive fixed and pay floating to stabilize sales revenue.',
       'Before another firm signs a new contract, the shape of the forward curve changes. Would its quote be lower?','settlement'),
      chapter('5 · From contango to backwardation','Predict a swap-rate change from the actual forward-price changes and their weights—not from a curve label alone.',
       'Maya compares two possible markets for a new equal-quantity swap. The original curve rises from $72 to $84 (contango). In the new scenario the first forward stays at $72, but later forwards fall to $68, $64 and $60 (backwardation). Rates and quantities are held fixed.',
       'In this particular change, what happens to the fair fixed price?', ['It falls: later forwards fall and none rises','It rises because the curve is backwardated','Its direction cannot be determined from these supplied prices'],0,
       'Every forward has a positive discounted-quantity weight. Here one is unchanged and the other three fall, so the weighted average must fall.',
       'The discounted products and their sums are supplied. Calculate the new quotient once. Then test whether the label “backwardation” alone is enough to predict the swap rate.',
       ['Year','Old F','New F','D','Old D × F','New D × F'],
       [[i+1,F[i],BACK[i],D[i],F[i]*D[i],BACK[i]*D[i]] for i in range(4)]+[['Total','','',sum(D),sum(f*d for f,d in zip(F,D)),sum(f*d for f,d in zip(BACK,D))]],
       r'\Delta K=\frac{\sum_jD_j\Delta F_j}{\sum_jD_j}\quad\text{(equal quantities; unchanged discount factors)}',
       [task('New fixed price ($/barrel)',KB,f'{sum(f*d for f,d in zip(BACK,D)):.2f} / 3.67','The denominator is unchanged. The numerator is smaller.')],
       f'With the first forward anchored at $72, K falls from ${K:.4f} to ${KB:.4f}. A different backwardated curve could sit at a higher overall level, so curve shape alone does not determine the direction of the rate change.',
       'Maya understands the price. She now asks whether the fixed payments can be moved to a single date.','curve'),
      chapter('6 · One fixed payment, four floating receipts','Price a nonstandard swap by matching present values and distinguish fair value from funding needs.',
       'Riverside negotiates a new version of the original equal-quantity hedge: it still receives the floating oil price on 10,000 barrels at each of four annual dates, but makes only one fixed payment at year 4. What total payment is fair?',
       'Should the single payment simply equal the sum of the four forward-price commitments?', ['No: payment timing must be reflected through discounting','Yes: the same oil purchases are covered'],0,
       'The contract exchanges cash flows at different dates. First value the floating leg through its forward-equivalent commitments, then find one fixed payment with the same present value.',
       'We have discounted each forward-equivalent purchase below. Their sum is the value the single fixed payment must match. Divide that present value by the year-4 discount factor, then check by discounting back.',
       ['Year','Forward ($/barrel)','Quantity (barrels)','D','PV of commitment ($)'],
       [[i+1,F[i],10000,D[i],F[i]*10000*D[i]] for i in range(4)]+[['Total PV','','','',PV]],
       r'PV_{float}=\sum_jD_jQ_jF_j,\qquad X_4=\frac{PV_{float}}{D_4},\qquad D_4X_4=PV_{float}',
       [task('Single fixed payment at year 4 ($)',PV/.86,f'{PV:.2f} / 0.86','This is a total dollar payment, not a per-barrel rate.',1)],
       f'The fair year-4 fixed payment is ${PV/.86:,.2f}. Multiplying by 0.86 returns ${PV:,.2f}. Floating receipts are still uncertain; forwards are used to value them. Physical purchases and matching floating receipts cancel at each date, leaving the one fixed obligation. The timing of cash needs and counterparty exposure has changed.',
       'You can now price both a standard level-price swap and a swap with a single fixed payment. Next, consider an existing contract and the risks it leaves behind.','payment'),
      chapter('7 · The old price stays fixed','Distinguish the fixed contract price from the swap’s current replacement value.',
       f'Return to Riverside’s original level-price swap at ${K:.4f}. Before any payment has occurred, all four current forward prices rise by $5. Quantities and discount factors are unchanged. The contract’s K does not reset.',
       'What is the old contract worth to Riverside, the fixed payer?', ['A positive amount: it retains cheaper terms than a new swap','Zero: the price was fair at inception','A negative amount because oil is more expensive'],0,
       'A new swap now requires a fixed price $5 higher. The old fixed payer owns favorable terms, though the physical oil purchases have also become more expensive.',
       'A $5 rise at every date raises the replacement rate by exactly $5. The discounted quantity is 10,000 × 3.67 = 36,700 barrels. Multiply the advantage per barrel by discounted quantity.',
       ['Old contract K','Replacement K','Difference ($/barrel)','Discounted quantity'],
       [[K,K+5,5,36700]],
       r'V_{payer}=\sum D_jQ_j(F_j-K_{old})=(K_{new}-K_{old})\sum D_jQ_j',
       [task('Value to Riverside ($)',value,'5 * 36700','A positive value is an asset to the fixed payer.',1)],
       'The old swap is an asset worth $183,500 to Riverside under the clean valuation assumptions. The other party has the opposite value. This does not mean the firm gained $183,500 on its combined physical and derivative exposure.',
       'The matching purchase assumptions were crucial. What if the refinery needs less oil than expected?','value'),
      chapter('8 · When the match breaks','Identify the remaining exposure when physical quantity or price differs from the swap.',
       f'A shutdown reduces one purchase to 8,000 barrels, but the swap still covers 10,000. At that settlement the oil index is $85 and the fixed price remains ${K:.4f}. Maya asks whether the per-barrel purchase cost is still fixed.',
       'Is this still an exact hedge of the physical purchase?', ['No: 2,000 barrels of swap exposure have no matching purchase','Yes: the fixed price did not change'],0,
       'The excess swap quantity gains when the index exceeds K and loses when the index is below K. An outcome can look favorable while risk remains.',
       'The physical purchase costs 8,000 × $85 = $680,000. The swap receipt is based on the contracted 10,000 barrels, not 8,000. Its dollar receipt is supplied; divide the net cost by actual barrels.',
       ['Actual barrels','Swap barrels','Physical cost ($)','Swap receipt ($)','Net cost ($)'],
       [[8000,10000,680000,10000*(85-K),buyer_cost(85,85,K,8000,10000)]],
       r'c=\frac{Q_{actual}S_{physical}-Q_{swap}(S_{index}-K)}{Q_{actual}}',
       [task('Effective cost per actual barrel ($)',buyer_cost(85,85,K,8000,10000)/8000,f'{buyer_cost(85,85,K,8000,10000):.6f} / 8000','Use actual physical barrels in the denominator.')],
       'The favorable extra swap receipt makes effective cost lower than K in this state. If oil were below K, the excess hedge would hurt. Even with matching quantities, a physical price $3 above the swap index would leave effective cost K + $3: basis risk. Funding and counterparty risk also remain.',
       'The core pricing work used supplied forwards. The next two short extensions examine where those inputs come from.','risk'),
      chapter('9 · Why the curve has its shape','Connect financing, storage and the benefit of inventory to a commodity forward price.',
       'Maya asks why a forward need not equal today’s spot price. Use a separate carry illustration: spot oil is $72, the continuous financing rate is 4%, proportional storage cost is 1.5%, and the convenience yield is 2.5% per year.',
       'Holding spot, financing and storage fixed, what does a larger convenience yield do to the forward price?', ['Lowers it: owning physical inventory becomes more beneficial','Raises it: every yield increases the forward price'],0,
       'Convenience yield represents the benefit of having inventory available. It offsets financing and storage costs in this stylized model.',
       'Net carry is 4% + 1.5% − 2.5% = 3% per year. For one year, grow spot by exp(0.03). The exponential factor is supplied, so only one multiplication remains.',
       ['Spot ($/barrel)','Financing r','Storage u','Convenience y','exp(net carry × time)'],
       [[72,.04,.015,.025,math.exp(.03)]],
       r'F=S_0e^{(r+u-y)T},\qquad y=r+u-\ln(F/S_0)/T',
       [task('One-year forward ($/barrel)',forward,'72 * EXP(0.03)','A positive net carry places the forward above spot.')],
       f'The forward is ${forward:.4f}. If convenience yield rises above financing plus storage, net carry becomes negative and the forward is below spot. Neither result is automatically a forecast of future spot. For an index, the corresponding relationship is F = S₀ exp[(r − dividend yield)T].',
       'Beyond the supplied curve, the dealer must make assumptions about such carry relationships.','carry'),
      chapter('10 · Quote beyond the available curve','Separate a modeled long-dated swap quote from a directly supplied market input.',
       'Riverside asks for six annual purchases, but the original supplied forwards stop at year 4 at $84. For years 4–6 only, assume incremental net carry of 3% per year. The year-5 and year-6 discount factors are supplied as 0.82 and 0.78. This is an explicit modeling assumption.',
       'Should Maya regard the resulting six-date fixed price as an observed market quote?', ['No: the last two forwards depend on an assumption','Yes: a precise formula makes every input observable'],0,
       'A model can produce a precise answer even when important inputs are uncertain. The long end must be disclosed and stressed.',
       'The first extension is worked: year-5 F = 84 exp(0.03 × 1). The year-6 price uses two additional years, not six. Both products are provided so you can price the six-date swap with the familiar quotient.',
       ['Year','F ($/barrel)','Source','D','D × F'],
       [[i+1,(F+ex)[i],'Supplied' if i<4 else 'Modeled',ds[i],(F+ex)[i]*ds[i]] for i in range(6)]+[['Total','','',sum(ds),sum(a*b for a,b in zip(F+ex,ds))]],
       r'F(0,T)=F(0,4)e^{0.03(T-4)},\qquad K_6=\frac{\sum_{j=1}^6D_jF_j}{\sum_{j=1}^6D_j}',
       [task('Six-date fixed price ($/barrel)',six,f'{sum(a*b for a,b in zip(F+ex,ds)):.9f} / {sum(ds):.2f}','Equal quantities still cancel, even when some forwards are modeled.')],
       f'The quote is ${six:.4f} per barrel under this assumption. Higher assumed convenience yield would reduce net carry, the two extended forwards, and the swap quote. Maya should compare assumptions rather than mistake precision for certainty.',
       'Finish by advising Maya on curve behavior and a new single-payment quote without the worked steps.','extrapolation')
    ]

# Riverside Refinery: Commodity Swap Studio v2.1

This revision follows one hypothetical refinery through a sequence of business decisions. It preserves v2.0 in its own folder and retains the spreadsheet engine only as optional practice.

## Open the studio

Double-click **Launch Riverside Studio.cmd** and open **http://localhost:8783**. The previous v2.0 can continue on port 8782. The launcher uses this folder's `.venv`, the existing course Python environment if present, or Python on PATH.

For a fresh installation, use Python 3.12 or later:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py --server.port 8783
```

## The teaching experience

Each chapter initially presents only an objective, Maya's business decision and one prediction. **See what happens** opens a worked explanation and a mostly completed table. Students finish one decisive calculation (two short entries in chapters 1–2), then explain the result through the story's conclusion. They can enter a number or an arithmetic expression directly—no spreadsheet entry is required.

After a correct response, **Next decision** continues the story. If stuck, **Need a nudge?** offers an explanation and an explicit walkthrough. This is ungraded practice, so a requested walkthrough also enables continuation. **Retry this chapter** clears that chapter. A collapsed sidebar journey allows direct navigation. **Explore further** contains full spreadsheets; these are separate optional practice examples, sometimes with different data.

The core route is chapters 1–6. After chapter 6, students can go directly to **Advise Maya**, the final debrief. Chapters 7–8 extend the business decisions; 9–10 examine pricing inputs and model assumptions. Each student entry belongs to the current Streamlit session and is not saved as an assignment or grade. Optional spreadsheet entries may persist in the browser tab's session storage. No student identity is requested.

| Chapter | Economic purpose | Required entries |
|---|---|---|
| 1. Protect one purchase | A negative derivative settlement can be part of a successful hedge | Two cells' results |
| 2. Four prices into one | Equate PVs; equal quantities cancel but discount factors do not | One product, one rate |
| 3. Buy more in one year | More quantity gives that dated forward more influence | One rate |
| 4. A payment is not failure | Combine physical cost and signed swap settlement | One dollar cost |
| 5. Contango to backwardation | Compare actual price changes, not just slope labels | One rate, then an interpretation |
| 6. One fixed payment | Match the PV of several floating-equivalent amounts | One dollar payment |
| 7. Old price stays fixed | Separate contractual price and replacement value | One dollar value |
| 8. When the match breaks | Recognize quantity and basis exposure | One effective cost |
| 9. Why the curve has its shape | Financing, storage and convenience yield | One forward price |
| 10. Beyond the available curve | Distinguish supplied and modeled inputs | One rate |
| 11. Advise Maya | Independent transfer: curve shape, rate, single payment, parallel shift | Two calculations and two interpretations |

## Two central outcomes

**Curve behavior:** With positive discounted-quantity weights, lowering some forwards while holding the others fixed lowers the fair rate. The anchored example moves from [72, 76, 80, 84] to [72, 68, 64, 60], with unchanged quantities and discount factors. A second backwardated curve, [92, 88, 84, 80], demonstrates that shape alone is insufficient: its higher price level gives a higher fixed rate than the original contango curve. A parallel price increase passes through one-for-one when weights are held fixed. None of these forward curves is labeled a spot forecast.

**Nonstandard swaps:** Value all floating-equivalent commitments using dated forwards and discount factors; divide that PV by the single fixed-payment date's discount factor. The fixed amount is dollars, not dollars per barrel. A comparison of year-1 and year-4 payment dates shows equal inception PV with different nominal amounts and funding timing.

## Conventions and sources

All data and the refinery story are hypothetical. Core forwards are [72, 76, 80, 84] dollars per barrel; discount factors are [0.97, 0.94, 0.90, 0.86]. These transparent rounded inputs are supplied directly. Interest rates in carry exercises use continuous compounding. The level rate is K, corresponding to S-bar in the course notes; D corresponds to P(0,t). Model assumptions exclude fees and credit adjustments, use matching reference prices and dates unless explicitly relaxed, and do not model futures daily marking-to-market.

The course syllabus's problem → payoff → economic idea → pricing → application approach, and the commodity-swap slides in `chapter_03_hedging_swaps/lecture_notes/Hedging2.pdf`, provide the course foundation. The continuing story, scaffolded tasks and final debrief are new exposition. V2.0 supplies the optional worksheet engine and supplementary practice modules.

## Deployment

Place the contents of this folder in a dedicated GitHub repository, preserving `.streamlit/config.toml`. On Streamlit Community Cloud, select `app.py` and a compatible Python version. With the full course repository, use `chapter_03_hedging_swaps/studio/Commodity_Swap_Learning_Studio_v2.1/app.py`; ensure the theme/telemetry settings are also present in the repository-root `.streamlit/config.toml`. Include `worksheet.html`, `formula.js`, and all Python modules.

Add the resulting public URL to Canvas as an external link opening in a new tab. Test the deployed prediction, calculation and navigation flow before sharing. This package does not publish the app automatically.

## Developer verification

`python -m unittest discover -s tests` checks the financial benchmarks, all story stages, saved answers, retry, and final assessment. `node tests/test_browser.cjs` uses Playwright and installed Edge to exercise the visible story at port 8783. Set `STUDIO_PLAYWRIGHT` to an existing Playwright package path if necessary. Node is a testing dependency only; the app requires only the Python packages listed in `requirements.txt`.


### Calculation-entry correction — September 9, 2026

Arithmetic entries accept an optional leading `=` in both the story and worksheets. Press Enter or click outside an entry to calculate. Story boxes retain the expression and show its numerical result below; worksheets display the result in the cell and retain the expression in the formula bar. Cell references and range functions are available inside worksheets. Each story answer receives explicit Correct, Not correct yet, Still blank, or Could not calculate feedback. A correct answer is acknowledged independently of other unfinished fields.

Regression checks cover `285.52/3.67`, optional equals and spaces, blank companion fields, invalid arithmetic, worksheet references and fill-down, and the complete ten-chapter journey.

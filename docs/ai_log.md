# AI Assistance Log

This log records assistance used during development. The entries distinguish prior student-reported tests from new changes that still require local execution. Update the result field after each real test. Do not invent terminal output.

| # | Date | Question / task | AI suggestion or change | Actual result / evidence | Assessment and next action |
|---|---|---|---|---|---|
| 1 | 2026-11-16 | Help build the Monte Carlo module | Explained historical bootstrap and created validation for returns, investment, days, simulations, and seed | Student previously reported `py_compile` and module execution passed | Reported PASS at that earlier revision; rerun after integration changes |
| 2 | 2026-11-16 | Help build risk assessment and report | Added probability of loss, percentile VaR, MDD, and TXT report generation | Student previously reported `python3 -m py_compile risk_report.py` and direct module run passed | Reported PASS at that earlier revision; rerun after integration changes |
| 3 | 2026-11-16 | Integrate the three members' modules | Connected data, simulation, and risk-report functions through `main.py` | Student previously reported the end-to-end AAPL workflow passed | Reported PASS at that earlier revision; current revision requires a new full run |
| 4 | 2026-11-17 | Check compliance with PE104 menu requirement | AI review found the existing menu used option 3 to exit, conflicting with the supplied rubric requiring option 0 | Confirmed directly in the repository's previous `main.py`; corrected in commit de15f69 | **AI design mistake / rubric mismatch identified during review.** Menu now exits on 0; student must run T01 and T02 |
| 5 | 2026-11-17 | Clarify whether sample_data should be example data | AI review found live downloads were being written to `sample_data/stock_prices.csv`, mixing cache and bundled example data | Confirmed in the previous `main.py` and `data_analysis.py`; workflow changed to cache live data under `data/cache/` and use sample CSV only for offline demo | **AI design mistake identified during review.** Run T04 and confirm sample CSV remains unchanged |
| 6 | 2026-11-17 | Repair empty project documentation | Wrote README with run instructions, dependencies, methods, limitations, and module ownership | README update committed as 19a3fc8; not yet reviewed by student | Awaiting student review and local run |
| 7 | 2026-11-17 | Document external packages | Added `yfinance` to requirements and explained standard-library modules | requirements update committed as 7af7dd1 | Installation test still required |
| 8 | 2026-11-17 | Add reproducible test evidence | Created a test plan with menu, invalid input, offline demo, report retrieval, missing report, and live-data cases | Test cases documented; none of the new revision's cases have been run locally yet | Run tests T01–T08 and replace pending results with actual observations |

## Notes
- “Student previously reported PASS” refers to the earlier revision, not the current repository state.
- The two AI design mistakes above are real mismatches found by inspecting the prior code against the supplied requirements. Keep these entries only if they accurately reflect the development discussion.
- AI output must be tested. The student remains responsible for understanding and explaining every line.

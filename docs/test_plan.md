# Test Plan and Results

**Important:** The code changes in this repository have been committed, but the updated program has not yet been executed on the student's Mac. Do not mark any test PASS until it is run locally and the observed result is entered below.

| ID | Test | Input / setup | Expected result | Actual result | Status |
|---|---|---|---|---|---|
| T01 | Exit menu | Start program, enter `0` | Goodbye message; program ends | Pending local run | NOT RUN |
| T02 | Invalid menu choice | Enter `9`, then `0` | Invalid-option message; menu repeats | Pending local run | NOT RUN |
| T03 | Invalid investment | Choose demo; enter `abc`, then a positive number | Error message, then re-prompt | Pending local run | NOT RUN |
| T04 | Offline sample analysis | Choose `3`; enter investment `10000`, days `10`, simulations `100` | Loads AAPL sample data without network; prints volatility and risk report; saves report | Pending local run | NOT RUN |
| T05 | Previous report | Run T04, return to menu, choose `2` | Previously saved report is displayed | Pending local run | NOT RUN |
| T06 | Missing report | Temporarily rename or remove `reports/risk_report.txt`; choose `2` | Friendly message; program continues | Pending local run | NOT RUN |
| T07 | Live ticker with network | Choose `1`; enter a valid ticker and positive values | Downloads or uses cache and generates report | Pending local run | NOT RUN |
| T08 | Invalid ticker / no network | Disable network and request an uncached ticker | Clear no-data message; program does not crash | Pending local run | NOT RUN |

## How to record results
1. Run `python3 main.py` from the project root.
2. Execute each case exactly as written.
3. Replace “Pending local run” with the observed output, including any error.
4. Change status to PASS or FAIL only after observing the result.
5. If a test fails, record the bug, fix, and retest result. Do not claim a test passed because code inspection suggests it should pass.

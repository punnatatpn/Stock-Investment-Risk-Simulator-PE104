import csv 
import datetime #ตรวจวันที่เเละเเปลงวันที่เป็นรูปเเบบมาตรฐาน
import logging #เป็นโมดูลที่ใช้สำหรับบันทึกเหตุการณ์หรือข้อความในโปรแกรม จากyfinance
import math #ตรวจว่าราคาเป็นตัวเลขที่มีค่าจำกัดหรือไม่ หรือนำเข้าโมดูลทางคณิตศาสตร์โดยไม่ต้องเขียนสูตรขึ้นเอง
import os #ตรวจสอบเส้นทาง（Path) ค้นหาโฟลเดอร์ที่เก็บไฟล์ CSV เเทนที่ไฟล์ด้วย os replace() 
import tempfile #สร้างไฟล์ชั่วคราวก่อนเเทนcsvจริง 

import yfinance as yf#มาจากเเพ็กเกจภายนอก yfinance ที่เราติดตั้งบน requirements.txt ใช้ข้อมูลราคาจาก Yahoo Finance


def load_stock_data(file_path, ticker):
    """Refresh one ticker's daily Close history, then load its CSV records."""
    selected_ticker = ticker.strip().upper()
    if not selected_ticker:#ตรวจสอบว่าผู้ใช้ไม่ได้ป้อนสัญลักษณ์หุ้นหรือไม่
        print("Error: Please enter a stock ticker.")
        return []

    storage_ticker = (
        #กำหนดชื่อticker ที่จะเก็บในcsv ถ้า ticker ลงท้ายด้วย .BK ให้ตัด .BK ออก มิฉะนั้นให้ใช้ ticker เดิม
        selected_ticker[:-3]
        if selected_ticker.endswith(".BK") #endswith() (string method) ใช้ถามว่า “ข้อความนี้ลงท้ายด้วยคำที่กำหนดหรือไม่” ผลที่ได้เป็น True หรือ False
        else selected_ticker 
    )
    symbols = (
        #สร้างชื่อที่จะลองค้นหาใน Yahoo Finance เช่นPTT.BK จะค้นชื่อเดียว ถ้าไม่มีจะลองค้นหาทั้งสองแบบ
        [selected_ticker]
        if "." in selected_ticker
        else [selected_ticker, f"{selected_ticker}.BK"]
    )
    downloaded_records = [] #เก็บราคาที่ดึงมา
    resolved_symbol = None #เก็บticker ที่พบ
    yfinance_logger = logging.getLogger("yfinance")#ขอ logger ที่ชื่อ "yfinance" จากโมดูล logging แล้วเก็บไว้ใน yfinance_logger ตัว logger ใช้ควบคุมข้อความสถานะ/คำเตือนที่ไลบรารี yfinance ส่งออกมา
    previous_log_level = yfinance_logger.level#จำระดับการแสดงข้อความเดิมไว้ใน previous_log_level เพื่อคืนค่าเดิมภายหลัง
    yfinance_logger.setLevel(logging.CRITICAL)
    #ตั้งระดับไว้ที่ CRITICAL 50 ซึ่งเป็นระดับสูงสุด ซ่อนข้อความระดับต่ำกว่า เช่น WARNING ระหว่างลองค้น ticker 
    #ถ้าลองค้น PTT แล้วไม่พบ ก่อนจะลอง PTT.BK yfinance อาจพิมพ์ข้อความแจ้งความผิดพลาดออกมา 

    try:#เริ่มบล็อคที่อาจเกิดข้อผิดพลาดระหว่างดึงข้อมูลเเละวนลองticker
        for symbol in symbols:#วนค้นหาtickerทุกตัวในsymbols 
            try:#เริ่มดักข้อผิดพลาดเฉพาะการดึงข้อมูลของ ticker ปัจจุบัน
                history = yf.Ticker(symbol).history( 
                    #ขอข้อมูลราคาหุ้นจาก Yahoo Finance #method ที่ใช้ร่วมกับ yf.Ticker คือ history():ดึงข้อมูลราคาหุ้นย้อนหลัง(เปิด สูง ต่ำ ปิด วอลุ่ม)
                    period="5y", #period คือพารามิเตอร์กำหนดช่วงเวลาของข้อมูลราคาหุ้นที่ต้องการดึงมาใช้งาน นับย้อนจากวันปัจจุบัน
                    #ค่า valueที่ใส่ในperiod ได้มี เลขd, เลขmo, เลขy, ytd:ตั้งเเต่ต้นปีปัจจุบันถึงวันนี้
                    interval="1d", #interval พารามิเตอร์กำหนดค.ถี่ 
                    #ค่าvalueที่ใส่ได้ เลขm:ระดับนาที, เลขh:ระดับชม., เลขd:ระดับวัน, เลขwk:ระดับสัปดาห์, เลขmo:ระดับเดือน 
                    # **ความสัมพันธ์กับค่า periodโดย 1m=ดึงย้อนหลังไม่เกิน7วัน/2m-9m=ดึงย้อนหลังไม่เกิน60วัน/1h=ดึงย้อนหลังไม่เกิน2ปี/1d=ดึงย้อนหลังได้ตั้งเเต่เข้าตลาด
                    auto_adjust=False,
                    #พารามิเตอร์ที่สั่งให้ปิดการปรับฐานราคาหุ้นอัตโนม้ติ ราคาที่ดึงมาจะเป็นราคาซื้อขายจริง ณ วันนั้นๆ  ไม่นำเงินปันผลเเละการเเตกพาร์มาคำนวณย้อนหลัง
                    #ตารางข้อมูลที่ได้จะมีคอลัม adj close เเยกเพิ่มมา เพื่อเเสดงราคาปิดปรับฐานต่างหาก                   
                    actions=False,#พารามิเตอร์ที่สั่งให้ซ่อน/ไม่ดึงคอลัมน์ข้อมูลเงินปันผลเเละการเเตกพาร์ **เหมาะกับข้อมูลที่ต้องการความกระชับ สะอาด นำไปคำนวณกราฟ
                )
            except Exception:#ดักจับข้อผิดพลาด คำสั่งนี้ใช้คู่กับtry เสมอ หากโค้ดในส่วนtry เกิดข้อผิดพลาด โปรเเกรมจะกระโดดมาส่วนนี้
                continue #ข้ามเเละลองตัวถัดไป

            if history.empty or "Close" not in history.columns:
                continue

            for price_date, raw_close in history["Close"].dropna().items():
                try:
                    close = float(raw_close)
                except (TypeError, ValueError):
                    continue

                if not math.isfinite(close) or close <= 0:
                    continue

                downloaded_records.append({
                    "date": price_date.strftime("%Y-%m-%d"),
                    "ticker": storage_ticker,
                    "close": round(close, 2),
                })

            if downloaded_records:
                resolved_symbol = symbol
                break
    finally:
        yfinance_logger.setLevel(previous_log_level)

    if downloaded_records:
        records_to_save = sorted(
            downloaded_records,
            key=lambda row: (row["ticker"].upper(), row["date"]),
        )
        temporary_path = None
        try:
            directory = os.path.dirname(os.path.abspath(file_path))
            with tempfile.NamedTemporaryFile(
                "w",
                newline="",
                encoding="utf-8",
                dir=directory,
                delete=False,
            ) as temporary_file:
                temporary_path = temporary_file.name
                writer = csv.DictWriter(
                    temporary_file,
                    fieldnames=["date", "ticker", "close"],
                )
                writer.writeheader()
                writer.writerows(
                    [
                        {**record, "close": f'{record["close"]:.2f}'}
                        if record["ticker"].upper() == storage_ticker
                        else record
                        for record in records_to_save
                    ]
                )
            os.replace(temporary_path, file_path)
        except OSError as error:
            print(f"Warning: Could not update the CSV cache: {error}")
            return downloaded_records
        finally:
            if temporary_path and os.path.exists(temporary_path):
                try:
                    os.remove(temporary_path)
                except OSError:
                    pass

        print(
            f"Replaced the CSV with {storage_ticker} from Yahoo Finance "
            f"({resolved_symbol}, Close); "
            f"latest available date: {downloaded_records[-1]['date']}."
        )
    else:
        print("Warning: Could not refresh from Yahoo Finance; trying the local CSV cache.")

    valid_records = []
    seen_dates = set()

    try:
        with open(file_path, "r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            required_fields = {"date", "ticker", "close"}
            if reader.fieldnames is None or not required_fields.issubset(reader.fieldnames):
                print("Error: CSV must contain date, ticker, and close columns.")
                return []

            for row_number, row in enumerate(reader, start=2):
                row_ticker = (row.get("ticker") or "").strip().upper()
                if row_ticker.removesuffix(".BK") != storage_ticker:
                    continue

                try:
                    price_date = datetime.datetime.strptime(
                        (row.get("date") or "").strip(), "%Y-%m-%d"
                    ).date()
                    close = float(row["close"])
                except (TypeError, ValueError):
                    print(f"Skipping row {row_number}: invalid date or close price.")
                    continue

                if not math.isfinite(close) or close <= 0:
                    print(f"Skipping row {row_number}: close must be a positive number.")
                    continue

                if price_date in seen_dates:
                    print(f"Skipping row {row_number}: duplicate date for {storage_ticker}.")
                    continue

                seen_dates.add(price_date)
                valid_records.append((price_date, {
                    "date": price_date.strftime("%Y-%m-%d"),
                    "ticker": storage_ticker,
                    "close": close,
                }))
    except (OSError, csv.Error) as error:
        print(f"Error reading CSV file: {error}")
        return []

    valid_records.sort(key=lambda item: item[0])
    return [record for _, record in valid_records]


def calculate_daily_returns(prices):
    """Return daily fractional changes for a sequence of positive prices."""
    try:
        numeric_prices = [float(price) for price in prices]
    except (TypeError, ValueError) as error:
        raise ValueError("Prices must all be numeric.") from error

    if any(not math.isfinite(price) or price <= 0 for price in numeric_prices):
        raise ValueError("Prices must all be finite numbers greater than zero.")

    daily_returns = []
    for index in range(1, len(numeric_prices)):
        previous_price = numeric_prices[index - 1]
        current_price = numeric_prices[index]
        daily_returns.append((current_price / previous_price) - 1)

    return daily_returns


if __name__ == "__main__":
    print("====================================")
    print("     QUANT STOCK RISK SIMULATOR")
    print("====================================")

    ticker = input("Enter stock ticker (e.g. AAPL or MC.BK): ").strip().upper()
    csv_path = os.path.join(os.path.dirname(__file__), "sample_data", "stock_prices.csv")
    stock_data = load_stock_data(csv_path, ticker)

    if not stock_data:
        print("No valid stock data found for", ticker)
    else:
        prices = [record["close"] for record in stock_data]
        daily_returns = calculate_daily_returns(prices)

        print("Selected Stock:", stock_data[0]["ticker"])
        print("Total Records:", len(stock_data))
        print("Latest Available Date:", stock_data[-1]["date"])
        print("\nStock Prices:")
        for record in stock_data:
            print(f'{record["date"]} | {record["ticker"]} | {record["close"]:.2f}')

        print("\nDaily Returns:")
        for index, daily_return in enumerate(daily_returns, start=1):
            print(f'{stock_data[index]["date"]} | {daily_return:.6%}')

        if daily_returns:
            average_daily_return = sum(daily_returns) / len(daily_returns)
            print(f"\nAverage Daily Return: {average_daily_return:.6%}")
        else:
            print("\nNot enough prices to calculate daily returns.")
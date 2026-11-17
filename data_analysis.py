import csv
import datetime
import logging
import math
import os
import tempfile

import yfinance as yf


def normalize_ticker(ticker):
    """
    ปรับรูปแบบ ticker ให้เป็นมาตรฐานของโปรเจกต์

    ตัวอย่าง:
    PTT.BK จะถูกเก็บเป็น PTT
    AAPL จะยังคงเป็น AAPL
    """

    return ticker.strip().upper().removesuffix(".BK")


def load_stock_data(file_path, ticker):
    """
    ดาวน์โหลดราคาปิดหุ้นย้อนหลังจาก Yahoo Finance
    บันทึกข้อมูลลง CSV และอ่านข้อมูลกลับมาใช้งาน

    ถ้าดาวน์โหลดไม่สำเร็จ จะลองใช้ข้อมูลจาก CSV เดิม
    """

    # ตรวจสอบ ticker ที่ผู้ใช้ป้อน
    if not isinstance(ticker, str) or not ticker.strip():
        print("Error: Please enter a valid stock ticker.")
        return []

    selected_ticker = ticker.strip().upper()
    storage_ticker = normalize_ticker(selected_ticker)

    # กำหนด ticker ที่จะลองค้นหาใน Yahoo Finance
    # เช่น ผู้ใช้กรอก PTT โปรแกรมจะลอง PTT และ PTT.BK
    if "." in selected_ticker:
        symbols = [selected_ticker]
    else:
        symbols = [selected_ticker, selected_ticker + ".BK"]

    downloaded_records = []
    resolved_symbol = None

    # ลดข้อความแจ้งเตือนจาก yfinance ชั่วคราว
    yfinance_logger = logging.getLogger("yfinance")
    previous_log_level = yfinance_logger.level

    try:
        yfinance_logger.setLevel(logging.CRITICAL)

        # ลองดาวน์โหลดข้อมูลทีละ ticker
        for symbol in symbols:
            try:
                history = yf.Ticker(symbol).history(
                    period="5y",
                    interval="1d",
                    auto_adjust=False,
                    actions=False
                )

            except Exception:
                # ถ้าดาวน์โหลด ticker นี้ไม่สำเร็จ ให้ลองตัวถัดไป
                continue

            # ตรวจสอบว่ามีข้อมูลและมีคอลัมน์ Close หรือไม่
            if history.empty or "Close" not in history.columns:
                continue

            # อ่านราคาปิดหุ้นทีละวัน
            for price_date, raw_close in history["Close"].dropna().items():

                try:
                    close = float(raw_close)

                except (TypeError, ValueError):
                    continue

                # ราคาต้องเป็นตัวเลขที่มีค่าจำกัดและมากกว่า 0
                if not math.isfinite(close) or close <= 0:
                    continue

                downloaded_records.append({
                    "date": price_date.strftime("%Y-%m-%d"),
                    "ticker": storage_ticker,
                    "close": close
                })

            # ถ้าดาวน์โหลดสำเร็จ ให้หยุดค้นหา
            if downloaded_records:
                resolved_symbol = symbol
                break

    finally:
        # คืนค่าระดับการแสดงข้อความเดิมของ yfinance
        yfinance_logger.setLevel(previous_log_level)

    # ถ้าดาวน์โหลดข้อมูลสำเร็จ
    if downloaded_records:

        # เรียงข้อมูลตามวันที่
        downloaded_records.sort(
            key=lambda record: record["date"]
        )

        existing_records = []

        # อ่านข้อมูลเดิมเพื่อเก็บหุ้นตัวอื่นไว้
        try:
            with open(file_path, "r", newline="", encoding="utf-8") as file:
                reader = csv.DictReader(file)

                required_fields = {"date", "ticker", "close"}

                if reader.fieldnames and required_fields.issubset(reader.fieldnames):

                    for row in reader:
                        old_ticker = (row.get("ticker") or "").strip().upper()

                        # ไม่เก็บข้อมูลหุ้นตัวที่กำลังดาวน์โหลดใหม่
                        if normalize_ticker(old_ticker) == storage_ticker:
                            continue

                        try:
                            old_date = datetime.datetime.strptime(
                                (row.get("date") or "").strip(),
                                "%Y-%m-%d"
                            ).date()

                            old_close = float(row["close"])

                        except (TypeError, ValueError):
                            continue

                        if not math.isfinite(old_close) or old_close <= 0:
                            continue

                        existing_records.append({
                            "date": old_date.strftime("%Y-%m-%d"),
                            "ticker": old_ticker,
                            "close": old_close
                        })

        except FileNotFoundError:
            # ถ้ายังไม่มี CSV ให้เริ่มสร้างไฟล์ใหม่
            pass

        except (OSError, csv.Error) as error:
            print("Warning: Could not read the previous CSV:", error)

        # รวมข้อมูลหุ้นตัวอื่นกับข้อมูลหุ้นที่เพิ่งดาวน์โหลด
        records_to_save = existing_records + downloaded_records

        # เรียงตาม ticker และวันที่
        records_to_save.sort(
            key=lambda record: (
                record["ticker"].upper(),
                record["date"]
            )
        )

        temporary_path = None

        try:
            # สร้างไฟล์ชั่วคราวในโฟลเดอร์เดียวกับ CSV
            # เพื่อให้ os.replace สามารถแทนที่ไฟล์ได้อย่างปลอดภัย
            directory = os.path.dirname(os.path.abspath(file_path))

            with tempfile.NamedTemporaryFile(
                mode="w",
                newline="",
                encoding="utf-8",
                dir=directory,
                delete=False
            ) as temporary_file:

                temporary_path = temporary_file.name

                writer = csv.DictWriter(
                    temporary_file,
                    fieldnames=["date", "ticker", "close"]
                )

                writer.writeheader()

                for record in records_to_save:
                    writer.writerow({
                        "date": record["date"],
                        "ticker": record["ticker"],
                        "close": format(record["close"], ".10f")
                    })

            # แทนที่ CSV เดิมด้วยไฟล์ใหม่
            os.replace(temporary_path, file_path)

        except OSError as error:
            print("Warning: Could not update the CSV cache:", error)

        finally:
            # ลบไฟล์ชั่วคราวถ้ายังเหลืออยู่
            if temporary_path and os.path.exists(temporary_path):
                try:
                    os.remove(temporary_path)
                except OSError:
                    pass

        print(
            f"Updated {storage_ticker} using Yahoo Finance "
            f"({resolved_symbol}, Close); "
            f"latest available date: {downloaded_records[-1]['date']}."
        )

    else:
        print(
            "Warning: Could not refresh from Yahoo Finance; "
            "trying the local CSV cache."
        )

    # อ่านข้อมูลจาก CSV เพื่อส่งกลับไปให้ main.py
    valid_records = []
    seen_dates = set()

    try:
        with open(file_path, "r", newline="", encoding="utf-8") as file:

            reader = csv.DictReader(file)

            required_fields = {"date", "ticker", "close"}

            # ตรวจสอบหัวตาราง CSV
            if (
                reader.fieldnames is None
                or not required_fields.issubset(reader.fieldnames)
            ):
                print(
                    "Error: CSV must contain date, ticker, and close columns."
                )
                return []

            # อ่านข้อมูลทีละแถว
            for row_number, row in enumerate(reader, start=2):

                row_ticker = (row.get("ticker") or "").strip().upper()

                # เลือกเฉพาะหุ้นที่ผู้ใช้ต้องการ
                if normalize_ticker(row_ticker) != storage_ticker:
                    continue

                try:
                    price_date = datetime.datetime.strptime(
                        (row.get("date") or "").strip(),
                        "%Y-%m-%d"
                    ).date()

                    close = float(row["close"])

                except (TypeError, ValueError):
                    print(
                        f"Skipping row {row_number}: "
                        "invalid date or close price."
                    )
                    continue

                # ตรวจสอบราคาหุ้น
                if not math.isfinite(close) or close <= 0:
                    print(
                        f"Skipping row {row_number}: "
                        "close must be a positive number."
                    )
                    continue

                # ตรวจสอบวันที่ซ้ำ
                if price_date in seen_dates:
                    print(
                        f"Skipping row {row_number}: "
                        f"duplicate date for {storage_ticker}."
                    )
                    continue

                seen_dates.add(price_date)

                valid_records.append({
                    "date": price_date.strftime("%Y-%m-%d"),
                    "ticker": storage_ticker,
                    "close": close
                })

    except (OSError, csv.Error) as error:
        print("Error reading CSV file:", error)
        return []

    # เรียงข้อมูลจากวันเก่าไปวันใหม่
    valid_records.sort(
        key=lambda record: record["date"]
    )

    return valid_records


def calculate_daily_returns(prices):
    """
    คำนวณผลตอบแทนรายวันจากราคาปิดหุ้น

    สูตร:
    Daily Return = (ราคาวันนี้ / ราคาวันก่อน) - 1
    """

    # ตรวจสอบว่าข้อมูลเป็น list หรือ tuple
    if not isinstance(prices, (list, tuple)):
        raise ValueError("Prices must be a list or tuple.")

    numeric_prices = []

    # แปลงราคาทุกตัวเป็น float
    for price in prices:

        # ป้องกัน Boolean ซึ่ง Python มองว่าเป็นตัวเลขได้
        if isinstance(price, bool):
            raise ValueError("Prices must be numeric values.")

        try:
            numeric_price = float(price)

        except (TypeError, ValueError) as error:
            raise ValueError(
                "Prices must all be numeric."
            ) from error

        # ราคาต้องเป็นตัวเลขที่มีค่าจำกัดและมากกว่า 0
        if not math.isfinite(numeric_price) or numeric_price <= 0:
            raise ValueError(
                "Prices must be finite numbers greater than zero."
            )

        numeric_prices.append(numeric_price)

    # ต้องมีราคาอย่างน้อย 2 วันจึงจะคำนวณผลตอบแทนได้
    if len(numeric_prices) < 2:
        return []

    daily_returns = []

    # คำนวณผลตอบแทนระหว่างวัน
    for index in range(1, len(numeric_prices)):

        previous_price = numeric_prices[index - 1]
        current_price = numeric_prices[index]

        daily_return = (current_price / previous_price) - 1

        daily_returns.append(daily_return)

    return daily_returns


# ส่วนนี้จะทำงานเมื่อเปิดไฟล์นี้โดยตรงเท่านั้น
# หาก main.py import ไฟล์นี้ ส่วนนี้จะไม่ทำงาน
if __name__ == "__main__":

    print("====================================")
    print("     QUANT STOCK RISK SIMULATOR")
    print("====================================")

    ticker = input(
        "Enter stock ticker (e.g. AAPL or MC.BK): "
    ).strip().upper()

    # เก็บข้อมูลที่ดาวน์โหลดไว้ใน cache แยกจาก sample_data
    cache_dir = os.path.join(
        os.path.dirname(__file__),
        "data",
        "cache"
    )
    os.makedirs(cache_dir, exist_ok=True)
    csv_path = os.path.join(cache_dir, "stock_prices.csv")

    stock_data = load_stock_data(csv_path, ticker)

    if not stock_data:
        print("No valid stock data found for", ticker)

    else:
        prices = [
            record["close"]
            for record in stock_data
        ]

        daily_returns = calculate_daily_returns(prices)

        print("Selected Stock:", stock_data[0]["ticker"])
        print("Total Records:", len(stock_data))
        print("Latest Available Date:", stock_data[-1]["date"])

        print("\nStock Prices:")

        for record in stock_data:
            print(
                f'{record["date"]} | '
                f'{record["ticker"]} | '
                f'{record["close"]:.4f}'
            )

        print("\nDaily Returns:")

        for index, daily_return in enumerate(daily_returns, start=1):
            print(
                f'{stock_data[index]["date"]} | '
                f'{daily_return:.6%}'
            )

        if daily_returns:
            average_daily_return = (
                sum(daily_returns) / len(daily_returns)
            )

            print(
                f"\nAverage Daily Return: "
                f"{average_daily_return:.6%}"
            )

        else:
            print(
                "\nNot enough prices to calculate daily returns."
            )
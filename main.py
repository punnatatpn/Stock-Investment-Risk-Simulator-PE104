"""ไฟล์หลักของโปรแกรม QUANT สำหรับเรียกใช้งานทุกส่วนผ่านเมนูหลัก"""

import csv
import math
import os

from data_analysis import load_stock_data, calculate_daily_returns
from simulation import calculate_volatility, run_monte_carlo
from risk_report import calculate_risk, generate_report


def get_ticker():
    """รับรหัสหุ้นจากผู้ใช้และตรวจสอบข้อมูลก่อนนำไปใช้"""
    while True:
        ticker = input("กรอกรหัสหุ้น (เช่น AAPL หรือ PTT.BK): ").strip().upper()
        if not ticker:
            print("กรุณากรอกรหัสหุ้น")
        elif not any(char.isalpha() for char in ticker):
            print("รหัสหุ้นต้องมีตัวอักษรอย่างน้อยหนึ่งตัว")
        elif not all(char.isalnum() or char == "." for char in ticker):
            print("ใช้ได้เฉพาะตัวอักษร ตัวเลข และจุดเท่านั้น")
        else:
            return ticker


def get_positive_float(prompt):
    """รับตัวเลขที่มากกว่าศูนย์ เช่น จำนวนเงินลงทุน"""
    while True:
        try:
            value = float(input(prompt).strip())
            if math.isfinite(value) and value > 0:
                return value
            print("กรุณากรอกตัวเลขที่มากกว่าศูนย์")
        except ValueError:
            print("ข้อมูลไม่ใช่ตัวเลข กรุณาลองใหม่")


def get_positive_integer(prompt):
    """รับจำนวนเต็มที่มากกว่าศูนย์ เช่น จำนวนวันหรือจำนวนรอบจำลอง"""
    while True:
        try:
            value = int(input(prompt).strip())
            if value > 0:
                return value
            print("กรุณากรอกจำนวนเต็มที่มากกว่าศูนย์")
        except ValueError:
            print("กรุณากรอกเป็นจำนวนเต็ม เช่น 10 หรือ 100")


def load_sample_data(sample_path, ticker="AAPL"):
    """อ่านราคาหุ้นจากไฟล์ CSV ตัวอย่าง และเลือกเฉพาะหุ้นที่ต้องการ"""
    records = []
    seen_dates = set()
    try:
        with open(sample_path, "r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            required = {"date", "ticker", "close"}
            if not reader.fieldnames or not required.issubset(reader.fieldnames):
                raise ValueError("ไฟล์ CSV ต้องมีคอลัมน์ date, ticker และ close")

            for row_number, row in enumerate(reader, start=2):
                if (row.get("ticker") or "").strip().upper() != ticker.upper():
                    continue
                try:
                    date = row["date"].strip()
                    close = float(row["close"])
                    if not math.isfinite(close) or close <= 0:
                        raise ValueError
                except (ValueError, TypeError, AttributeError):
                    print(f"ข้ามแถวที่ {row_number} เพราะข้อมูลไม่ถูกต้อง")
                    continue
                if date in seen_dates:
                    continue
                seen_dates.add(date)
                records.append({"date": date, "ticker": ticker.upper(), "close": close})
    except FileNotFoundError:
        print("ไม่พบไฟล์ข้อมูลตัวอย่าง:", sample_path)
        return []
    except (OSError, csv.Error, ValueError) as error:
        print("อ่านไฟล์ข้อมูลตัวอย่างไม่ได้:", error)
        return []

    records.sort(key=lambda item: item["date"])
    return records


def run_analysis(ticker_override=None, use_sample=False):
    """เรียกขั้นตอนวิเคราะห์ข้อมูล จำลองผลลัพธ์ ประเมินความเสี่ยง และสร้างรายงาน"""
    ticker = ticker_override or get_ticker()
    initial_investment = get_positive_float("จำนวนเงินลงทุนเริ่มต้น: ")
    trading_days = get_positive_integer("จำนวนวันที่ต้องการจำลอง: ")
    simulations = get_positive_integer("จำนวนรอบการจำลอง: ")
    confidence_level = 0.95

    base_dir = os.path.dirname(os.path.abspath(__file__))
    if use_sample:
        csv_path = os.path.join(base_dir, "sample_data", "stock_prices.csv")
        print("\nโหมดทดลอง: ใช้ข้อมูลตัวอย่างที่มีอยู่ในเครื่อง ไม่ต้องเชื่อมต่ออินเทอร์เน็ต")
        stock_data = load_sample_data(csv_path, ticker)
    else:
        cache_dir = os.path.join(base_dir, "data", "cache")
        os.makedirs(cache_dir, exist_ok=True)
        csv_path = os.path.join(cache_dir, "stock_prices.csv")
        print("\n[1/4] กำลังโหลดข้อมูลราคาหุ้นจาก Yahoo Finance...")
        stock_data = load_stock_data(csv_path, ticker)

    if not stock_data:
        print("ไม่มีข้อมูลหุ้นให้วิเคราะห์ กรุณาตรวจสอบรหัสหุ้นหรือไฟล์ข้อมูลตัวอย่าง")
        return None

    prices = [record["close"] for record in stock_data]
    daily_returns = calculate_daily_returns(prices)
    if len(daily_returns) < 2:
        print("ต้องมีข้อมูลราคาหุ้นที่ถูกต้องอย่างน้อย 3 รายการ")
        return None

    print("โหลดข้อมูลราคาหุ้นแล้ว:", len(stock_data), "รายการ")
    print("\n[2/4] กำลังคำนวณความผันผวน...")
    volatility_results = calculate_volatility(daily_returns)
    print("ความผันผวนต่อปี:", f"{volatility_results['annualized_volatility']:.2%}")

    print("\n[3/4] กำลังจำลองผลลัพธ์ด้วยวิธี Historical Bootstrap Monte Carlo...")
    simulation_paths = run_monte_carlo(
        daily_returns, initial_investment, trading_days, simulations
    )
    print("จำลองเสร็จแล้ว:", len(simulation_paths), "รอบ")

    risk_results = calculate_risk(
        simulation_paths, initial_investment, confidence_level
    )
    analysis = {
        "ticker": ticker,
        "initial_investment": initial_investment,
        "trading_days": trading_days,
        "simulations": simulations,
        "confidence_level": confidence_level,
        **volatility_results,
        **risk_results,
    }

    reports_dir = os.path.join(base_dir, "reports")
    os.makedirs(reports_dir, exist_ok=True)
    report_path = os.path.join(reports_dir, "risk_report.txt")
    report = generate_report(analysis, report_path)

    print("\n[4/4] สร้างรายงานเรียบร้อยแล้ว")
    print("\n" + report)
    print("\nบันทึกรายงานไว้ที่:", report_path)
    return analysis


def view_previous_report():
    """เปิดและแสดงรายงานความเสี่ยงที่เคยบันทึกไว้"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    report_path = os.path.join(base_dir, "reports", "risk_report.txt")
    if not os.path.exists(report_path):
        print("\nยังไม่มีรายงาน กรุณาวิเคราะห์หุ้นก่อน")
        return None
    try:
        with open(report_path, "r", encoding="utf-8") as file:
            report = file.read()
        if not report.strip():
            print("\nไฟล์รายงานยังไม่มีเนื้อหา")
            return None
        print("\n" + "=" * 60)
        print("รายงานความเสี่ยงครั้งก่อน")
        print("=" * 60)
        print(report)
        return report
    except OSError as error:
        print("\nเปิดรายงานไม่ได้:", error)
        return None


def main():
    """แสดงเมนูซ้ำไปเรื่อย ๆ จนกว่าผู้ใช้จะเลือก 0 เพื่อออกจากโปรแกรม"""
    while True:
        print("\n" + "=" * 50)
        print("       โปรแกรมจำลองความเสี่ยงการลงทุนในหุ้น QUANT")
        print("=" * 50)
        print("\nเมนูหลัก")
        print("[1] วิเคราะห์ความเสี่ยงของหุ้น (ดึงข้อมูลจาก Yahoo Finance)")
        print("[2] ดูรายงานครั้งก่อน")
        print("[3] ทดลองใช้งานด้วยข้อมูลตัวอย่าง (ไม่ต้องใช้อินเทอร์เน็ต)")
        print("[0] ออกจากโปรแกรม")

        choice = input("\nเลือกเมนูที่ต้องการ: ").strip()
        if choice == "1":
            try:
                run_analysis()
            except (ValueError, TypeError, OSError, KeyError) as error:
                print("\nไม่สามารถวิเคราะห์ข้อมูลได้:", error)
            except Exception as error:
                print("\nเกิดข้อผิดพลาดที่ไม่คาดคิด:", error)
            input("\nกด Enter เพื่อกลับไปยังเมนูหลัก...")
        elif choice == "2":
            view_previous_report()
            input("\nกด Enter เพื่อกลับไปยังเมนูหลัก...")
        elif choice == "3":
            try:
                run_analysis("AAPL", use_sample=True)
            except (ValueError, TypeError, OSError, KeyError) as error:
                print("\nไม่สามารถทดลองวิเคราะห์ได้:", error)
            except Exception as error:
                print("\nเกิดข้อผิดพลาดที่ไม่คาดคิด:", error)
            input("\nกด Enter เพื่อกลับไปยังเมนูหลัก...")
        elif choice == "0":
            print("\nขอบคุณที่ใช้โปรแกรม QUANT Stock Risk Simulator")
            print("ปิดโปรแกรมเรียบร้อยแล้ว")
            return 0
        else:
            print("\nไม่มีเมนูนี้ กรุณาเลือก 0, 1, 2 หรือ 3")


if __name__ == "__main__":
    main()

"""โมดูลคำนวณความผันผวนและจำลองมูลค่าเงินลงทุนด้วย Monte Carlo"""

import random
import math


def calculate_volatility(returns):
    """
    คำนวณความผันผวนจากผลตอบแทนรายวันในอดีต

    รับค่า:
        returns: รายการผลตอบแทนรายวัน เช่น [0.01, -0.02, 0.015]

    ส่งกลับ:
        dict: ค่าเฉลี่ยผลตอบแทน ความแปรปรวน ส่วนเบี่ยงเบนมาตรฐานรายวัน
              และความผันผวนต่อปี
    """

    if not isinstance(returns, (list, tuple)):
        raise TypeError("ข้อมูลผลตอบแทนต้องอยู่ในรูปแบบ list หรือ tuple")

    if len(returns) < 2:
        raise ValueError(
            "ต้องมีข้อมูลผลตอบแทนอย่างน้อย 2 ค่า จึงจะคำนวณความผันผวนได้"
        )

    if not all(
        isinstance(r, (int, float))
        and not isinstance(r, bool)
        and math.isfinite(r)
        and r >= -1
        for r in returns
    ):
        raise ValueError(
            "ข้อมูลผลตอบแทนต้องเป็นตัวเลขที่ถูกต้อง และต้องไม่ต่ำกว่า -1"
        )

    # หาค่าเฉลี่ยของผลตอบแทนรายวัน
    mean_return = sum(returns) / len(returns)

    # เก็บค่าความแตกต่างระหว่างผลตอบแทนแต่ละวันกับค่าเฉลี่ย ยกกำลังสอง
    squared_deviations = []

    for daily_return in returns:
        deviation = daily_return - mean_return
        squared_deviation = deviation ** 2
        squared_deviations.append(squared_deviation)

    # คำนวณความแปรปรวน โดยหารด้วยจำนวนข้อมูลลบหนึ่ง
    variance = sum(squared_deviations) / (len(returns) - 1)

    # ถอดรากที่สองของความแปรปรวน เพื่อหาความผันผวนรายวัน
    daily_std_dev = math.sqrt(variance)

    # แปลงความผันผวนรายวันเป็นรายปี โดยใช้ 252 วันทำการ
    annualized_volatility = daily_std_dev * math.sqrt(252)

    return {
        "mean_daily_return": mean_return,
        "variance": variance,
        "daily_std_dev": daily_std_dev,
        "annualized_volatility": annualized_volatility
    }


def run_monte_carlo(
    returns,
    initial_investment,
    trading_days,
    simulations,
    seed=42
):
    """
    จำลองมูลค่าเงินลงทุนหลาย ๆ รอบ ด้วยวิธี Historical Bootstrap Monte Carlo

    หลักการ:
        สุ่มเลือกผลตอบแทนรายวันจากข้อมูลในอดีต แล้วนำไปคำนวณมูลค่าเงินลงทุน
        ทำซ้ำตามจำนวนวันที่กำหนด และทำซ้ำหลายรอบตามจำนวนการจำลอง

    รับค่า:
        returns: ผลตอบแทนรายวันในอดีตที่ใช้เป็นข้อมูลสำหรับสุ่ม
        initial_investment: จำนวนเงินลงทุนเริ่มต้น
        trading_days: จำนวนวันที่ต้องการจำลองในแต่ละรอบ
        simulations: จำนวนรอบที่ต้องการจำลอง
        seed: ตัวเลขตั้งต้นสำหรับการสุ่ม ทำให้การทดลองซ้ำได้ผลเหมือนเดิม

    ส่งกลับ:
        list: รายการผลการจำลองทั้งหมด แต่ละรอบเก็บมูลค่าเงินลงทุนตั้งแต่วันแรก
              ไปจนถึงวันสุดท้าย
    """

    if not isinstance(returns, (list, tuple)) or len(returns) == 0:
        raise ValueError("ต้องใส่ข้อมูลผลตอบแทนอย่างน้อย 1 ค่า")

    if not all(
        isinstance(r, (int, float))
        and not isinstance(r, bool)
        and math.isfinite(r)
        and r >= -1
        for r in returns
    ):
        raise ValueError(
            "ข้อมูลผลตอบแทนต้องเป็นตัวเลขที่ถูกต้อง และต้องไม่ต่ำกว่า -1"
        )

    if (
        not isinstance(initial_investment, (int, float))
        or isinstance(initial_investment, bool)
        or not math.isfinite(initial_investment)
        or initial_investment <= 0
    ):
        raise ValueError(
            "เงินลงทุนเริ่มต้นต้องเป็นตัวเลขที่มากกว่าศูนย์"
        )

    if (
        not isinstance(trading_days, int)
        or isinstance(trading_days, bool)
        or trading_days <= 0
    ):
        raise ValueError("จำนวนวันจำลองต้องเป็นจำนวนเต็มที่มากกว่าศูนย์")

    if (
        not isinstance(simulations, int)
        or isinstance(simulations, bool)
        or simulations <= 0
    ):
        raise ValueError("จำนวนรอบจำลองต้องเป็นจำนวนเต็มที่มากกว่าศูนย์")

    if not isinstance(seed, int) or isinstance(seed, bool):
        raise ValueError("ค่า seed ต้องเป็นจำนวนเต็ม")

    # สร้างตัวสุ่ม โดยใช้ seed เพื่อให้ได้ผลการสุ่มซ้ำได้
    rng = random.Random(seed)

    # ใช้เก็บผลการจำลองของทุกรอบ
    all_simulations = []

    # วนทำซ้ำตามจำนวนรอบที่ผู้ใช้กำหนด
    for simulation in range(simulations):

        # เริ่มต้นแต่ละรอบด้วยเงินลงทุนตั้งต้น
        portfolio_values = [initial_investment]

        current_value = initial_investment

        # จำลองผลตอบแทนทีละวัน
        for day in range(trading_days):

            # สุ่มผลตอบแทนหนึ่งวันจากข้อมูลในอดีต
            daily_return = rng.choice(returns)

            # คำนวณมูลค่าเงินลงทุนใหม่หลังราคาหุ้นเปลี่ยนแปลง
            current_value = current_value * (1 + daily_return)

            # บันทึกมูลค่าเงินลงทุนของวันนั้น
            portfolio_values.append(current_value)

        # เมื่อจำลองครบทุกวันแล้ว เก็บผลของรอบนี้ไว้
        all_simulations.append(portfolio_values)

    # ส่งผลการจำลองทั้งหมดกลับไปให้ไฟล์อื่นนำไปวิเคราะห์ความเสี่ยงต่อ
    return all_simulations

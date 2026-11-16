# QUANT - ระบบจำลองการลงทุนในหุ้น
# MODULE 3: การประเมินความเสี่ยงและรายงานการลงทุน
# หน้าที่หลัก:
# 1. คำนวณความเสี่ยงจากผลการจำลอง
# 2. เอาผลที่ได้มาทำเป็นรายงาน TXT
import statistics  # เอาไว้หาค่าเฉลี่ยและคำนวณทางสถิติ
import math  # เอาไว้ใช้คำนวณพวกปัดเศษ
import os  # เอาไว้จัดการไฟล์กับโฟลเดอร์
from datetime import datetime  # เอาไว้ดึงวันและเวลาปัจจุบัน

# ฟังก์ชันที่ 1: หาค่าการลดลงสูงสุดของพอร์ต
def calculate_maximum_drawdown(path):  # รับข้อมูลพอร์ตจากการจำลองมา 1 รอบ
    running_peak = path[0]  # เอาค่าแรกมาเป็นจุดสูงสุดเริ่มต้น
    maximum_drawdown = 0.0  # ตั้งค่าเริ่มต้นไว้ที่ 0 ก่อน
    for current_value in path:  # วนดูมูลค่าพอร์ตไปทีละค่า
        if current_value > running_peak:  # ถ้าค่าตอนนี้สูงกว่าจุดสูงสุดเดิม
            running_peak = current_value  # ก็เปลี่ยนเป็นจุดสูงสุดใหม่
        if running_peak > 0:  # เช็คว่าจุดสูงสุดมากกว่า 0 ไหม
            drawdown = 1 - (current_value / running_peak)  # หาว่าพอร์ตลดลงไปเท่าไหร่
        else:
            drawdown = 0.0  # ถ้าค่าเป็น 0 ก็ให้การลดลงเป็น 0
        if drawdown > maximum_drawdown:  # ถ้าค่าที่ได้มากกว่าค่าสูงสุดเดิม
            maximum_drawdown = drawdown  # ก็เก็บค่าใหม่เอาไว้
    return maximum_drawdown  # ส่งค่าการลดลงสูงสุดกลับไป

# ฟังก์ชันที่ 2: ใช้หาค่าเปอร์เซ็นไทล์
def calculate_percentile(sorted_values, confidence_level):  # รับข้อมูลที่เรียงแล้วกับระดับความเชื่อมั่น
    n = len(sorted_values)  # นับว่ามีข้อมูลทั้งหมดกี่ตัว

    if n == 1:  # ถ้ามีข้อมูลแค่ตัวเดียว
        return float(sorted_values[0])  # ก็ส่งค่านั้นกลับไปเลย
    
    position = (n - 1) * confidence_level  # หาตำแหน่งของค่าที่เราต้องการ
    lower_index = math.floor(position)  # ปัดตำแหน่งลง
    upper_index = math.ceil(position)  # ปัดตำแหน่งขึ้น

    if lower_index == upper_index:  # ถ้าตำแหน่งที่ได้เป็นตัวเดียวกัน
        return float(sorted_values[lower_index])  # ก็ใช้ค่าตรงนั้นได้เลย

    fraction = position - lower_index  # หาระยะห่างของตำแหน่งที่ต้องการ
    lower_value = sorted_values[lower_index]  # เก็บค่าตัวล่างไว้
    upper_value = sorted_values[upper_index]  # เก็บค่าตัวบนไว้

    percentile = (
        lower_value
        + (upper_value - lower_value) * fraction  # คำนวณค่าที่อยู่ระหว่างสองตัวนี้
    )
    return float(percentile)  # ส่งค่าที่คำนวณได้กลับไป

# ฟังก์ชันที่ 3: ใช้คำนวณความเสี่ยงในการลงทุน
def calculate_risk(
    simulation_paths,  # รับผลการจำลองทั้งหมด
    initial_investment,  # รับจำนวนเงินที่ลงทุนไปตอนแรก
    confidence_level  # รับระดับความเชื่อมั่น เช่น 0.95
):
    # เช็คก่อนว่ามีข้อมูลส่งเข้ามาหรือเปล่า
    if not simulation_paths:
        raise ValueError("ไม่พบข้อมูลเส้นทางการจำลอง")  # ถ้าไม่มีข้อมูลก็แจ้งเตือน

    if initial_investment <= 0:  # เช็คว่าเงินลงทุนเริ่มต้นมากกว่า 0 ไหม
        raise ValueError("เงินลงทุนเริ่มต้นต้องมากกว่า 0")  # ถ้าไม่ถูกต้องก็แจ้งเตือน

    if not 0 <= confidence_level <= 1:  # เช็คว่าระดับความเชื่อมั่นอยู่ในช่วง 0 ถึง 1 ไหม
        raise ValueError("ระดับความเชื่อมั่นต้องอยู่ระหว่าง 0 ถึง 1")

    for path in simulation_paths:  # วนเช็คข้อมูลจำลองทีละรอบ

        if not path:  # ถ้ารอบไหนไม่มีข้อมูล
            raise ValueError("เส้นทางการจำลองต้องไม่เป็นค่าว่าง")  # ก็แจ้งเตือน

        for value in path:  # วนเช็คตัวเลขในแต่ละรอบ

            if not isinstance(value, (int, float)):  # เช็คว่าข้อมูลเป็นตัวเลขหรือเปล่า
                raise TypeError("ค่าภายในเส้นทางการจำลองต้องเป็นตัวเลข")

            if not math.isfinite(value) or value < 0:  # เช็คว่าตัวเลขไม่ผิดปกติและไม่ติดลบ
                raise ValueError("ค่าต้องเป็นตัวเลขที่ถูกต้องและไม่ติดลบ")

    # 1. หามูลค่าเงินลงทุนตอนจบของแต่ละรอบ
    final_values = [
        path[-1]  # เอาค่าตัวสุดท้ายของแต่ละรอบออกมา
        for path in simulation_paths
    ]
    average_final_value = statistics.mean(final_values)  # หาค่าเฉลี่ยของเงินลงทุนตอนจบ
    best_final_value = max(final_values)  # หาว่ารอบไหนได้เงินมากที่สุด
    worst_final_value = min(final_values)  # หาว่ารอบไหนได้เงินน้อยที่สุด

    # 2. หาว่ามีโอกาสขาดทุนกี่เปอร์เซ็นต์
    loss_count = sum(
        1  # เจอรอบที่ขาดทุนก็นับเพิ่ม 1
        for value in final_values
        if value < initial_investment  # เช็คว่าเงินตอนจบน้อยกว่าเงินที่ลงทุนไปไหม
    )

    probability_of_loss = (
        loss_count / len(final_values)  # เอาจำนวนรอบที่ขาดทุนหารด้วยจำนวนรอบทั้งหมด
    )

    # 3. คำนวณค่าความเสี่ยง VaR
    losses = [
        initial_investment - value  # เอาเงินลงทุนเริ่มต้นลบกับเงินตอนจบ
        for value in final_values
    ]

    losses.sort()  # เรียงค่าผลขาดทุนจากน้อยไปมาก

    var_value = calculate_percentile(
        losses,
        confidence_level  # ส่งข้อมูลผลขาดทุนกับระดับความเชื่อมั่นไปหาค่า VaR
    )

    # 4. หาค่าการลดลงสูงสุดของพอร์ต (MDD)
    maximum_drawdowns = [
        calculate_maximum_drawdown(path)  # หาค่า MDD ของแต่ละรอบ
        for path in simulation_paths
    ]

    average_mdd = statistics.mean(maximum_drawdowns)  # หาค่าเฉลี่ย MDD ของทุกรอบ
    worst_mdd = max(maximum_drawdowns)  # หารอบที่พอร์ตลดลงหนักที่สุด

    # 5. เอาผลที่คำนวณได้มาเก็บรวมกัน
    risk_results = {

        "average_final_value":
            float(average_final_value),  # เก็บค่าเฉลี่ยเงินลงทุนตอนจบ

        "best_final_value":
            float(best_final_value),  # เก็บเงินตอนจบที่มากที่สุด

        "worst_final_value":
            float(worst_final_value),  # เก็บเงินตอนจบที่น้อยที่สุด

        "probability_of_loss":
            float(probability_of_loss),  # เก็บโอกาสที่จะขาดทุน

        "var":
            float(var_value),  # เก็บค่าความเสี่ยง VaR

        "average_mdd":
            float(average_mdd),  # เก็บค่าเฉลี่ยการลดลงของพอร์ต

        "worst_mdd":
            float(worst_mdd)  # เก็บค่าการลดลงที่หนักที่สุด
    }

    return risk_results  # ส่งผลลัพธ์ทั้งหมดกลับไปให้ส่วนอื่นใช้

# ฟังก์ชันที่ 4: เอาผลที่ได้มาสร้างเป็นรายงาน
def generate_report(analysis, output_path):  # รับข้อมูลที่วิเคราะห์แล้วกับตำแหน่งที่จะเซฟไฟล์

    # เช็คก่อนว่าข้อมูลที่ต้องใช้ทำรายงานมีครบไหม
    required_keys = [
        "ticker",  # ชื่อหุ้น
        "initial_investment",  # เงินที่ลงทุนตอนแรก
        "trading_days",  # จำนวนวันซื้อขาย
        "simulations",  # จำนวนรอบที่จำลอง
        "confidence_level",  # ระดับความเชื่อมั่น
        "average_final_value",  # เงินลงทุนเฉลี่ยตอนจบ
        "best_final_value",  # เงินลงทุนที่มากที่สุด
        "worst_final_value",  # เงินลงทุนที่น้อยที่สุด
        "probability_of_loss",  # โอกาสขาดทุน
        "var",  # ค่าความเสี่ยง VaR
        "average_mdd",  # ค่าเฉลี่ย MDD
        "worst_mdd"  # ค่า MDD ที่มากที่สุด
    ]

    for key in required_keys:  # วนเช็คข้อมูลทีละตัว

        if key not in analysis:  # ถ้าหาข้อมูลตัวไหนไม่เจอ
            raise KeyError(
                f"ไม่พบข้อมูลที่จำเป็นในรายงาน: {key}"  # แจ้งว่าข้อมูลตัวไหนหายไป
            )


    # ดึงข้อมูลเพิ่มเติม ถ้ามีส่งมา
    mean_daily_return = analysis.get(
        "mean_daily_return"  # ดึงค่าผลตอบแทนเฉลี่ยรายวัน
    )

    annualized_volatility = analysis.get(
        "annualized_volatility"  # ดึงค่าความผันผวนต่อปี
    )

    # เริ่มสร้างเนื้อหาที่จะเอาไปใส่ในรายงาน
    report_lines = [
        "=" * 60,  # สร้างเส้นคั่นด้านบน
        "QUANT - ระบบจำลองการลงทุนในหุ้น",
        "รายงานการประเมินความเสี่ยงและผลการลงทุน",
        "=" * 60,
        f"วันที่จัดทำรายงาน: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",  # ใส่วันกับเวลาตอนที่สร้างรายงาน

        "",
        "ข้อมูลหุ้น",
        "-" * 60,
        f"ชื่อย่อหุ้น: {analysis['ticker']}",  # แสดงชื่อหุ้นที่เราเลือก

        "",
        "การตั้งค่าการจำลอง",
        "-" * 60,
        f"เงินลงทุนเริ่มต้น: {analysis['initial_investment']:,.2f}",  # แสดงเงินที่ใช้ลงทุน
        f"จำนวนวันซื้อขาย: {analysis['trading_days']}",  # แสดงจำนวนวันที่ใช้จำลอง
        f"จำนวนครั้งในการจำลอง: {analysis['simulations']}",  # แสดงว่าจำลองไปกี่รอบ
        f"ระดับความเชื่อมั่น: {analysis['confidence_level'] * 100:.2f}%",  # เปลี่ยน 0.95 ให้เป็น 95%

        "",
        "ผลการลงทุน",
        "-" * 60,
        f"มูลค่าเงินลงทุนเฉลี่ยเมื่อสิ้นสุด: {analysis['average_final_value']:,.2f}",  # แสดงเงินเฉลี่ยตอนจบ
        f"มูลค่าเงินลงทุนสูงสุด: {analysis['best_final_value']:,.2f}",  # แสดงเงินที่ได้มากที่สุด
        f"มูลค่าเงินลงทุนต่ำสุด: {analysis['worst_final_value']:,.2f}",  # แสดงเงินที่ได้น้อยที่สุด

        "",
        "การประเมินความเสี่ยง",
        "-" * 60,
        f"โอกาสที่จะขาดทุน: {analysis['probability_of_loss'] * 100:.2f}%",  # แสดงโอกาสขาดทุนเป็นเปอร์เซ็นต์
        f"มูลค่าความเสี่ยง (VaR): {analysis['var']:,.2f}",  # แสดงค่า VaR
        f"ค่าเฉลี่ยการลดลงสูงสุดของพอร์ต (MDD): {analysis['average_mdd'] * 100:.2f}%",  # แสดงค่าเฉลี่ย MDD เป็นเปอร์เซ็นต์
        f"การลดลงสูงสุดของพอร์ต: {analysis['worst_mdd'] * 100:.2f}%",  # แสดงค่า MDD ที่มากที่สุด
    ]

    # ถ้ามีข้อมูลผลตอบแทนรายวันก็เพิ่มเข้าไปในรายงาน
    if mean_daily_return is not None:
        report_lines.append(
            f"ผลตอบแทนเฉลี่ยรายวัน: {mean_daily_return * 100:.4f}%"  # แปลงค่าเป็นเปอร์เซ็นต์แล้วเพิ่มเข้าไป
        )

    # ถ้ามีข้อมูลความผันผวนต่อปีก็เพิ่มเข้าไปเหมือนกัน
    if annualized_volatility is not None:
        report_lines.append(
            f"ความผันผวนต่อปี: {annualized_volatility * 100:.2f}%"  # แสดงค่าความผันผวนเป็นเปอร์เซ็นต์
        )

    # เพิ่มหมายเหตุไว้ท้ายรายงาน
    report_lines.extend([
        "",
        "หมายเหตุของรายงาน",
        "-" * 60,
        "1. ค่า VaR คำนวณจากการกระจายตัวของผลขาดทุนจากการจำลอง",
        "2. โอกาสที่จะขาดทุนแสดงสัดส่วนของการจำลองที่มีมูลค่าเงินลงทุนสุดท้ายต่ำกว่าเงินลงทุนเริ่มต้น",
        "3. ค่า Maximum Drawdown แสดงการลดลงของมูลค่าพอร์ตจากจุดสูงสุดที่ผ่านมา",
        "4. ค่า Drawdown แสดงผลเป็นเปอร์เซ็นต์ในรูปแบบค่าบวก",
        "5. ผลการจำลองไม่สามารถรับประกันผลตอบแทนจากการลงทุนในอนาคตได้",
        "=" * 60
    ])
    report_text = "\n".join(report_lines)  # เอาข้อความทุกบรรทัดมาต่อกันเป็นรายงานเดียว

    # เตรียมโฟลเดอร์สำหรับเก็บรายงาน
    directory = os.path.dirname(
        os.path.abspath(output_path)  # หาตำแหน่งเต็มของไฟล์ที่จะบันทึก
    )

    os.makedirs(directory, exist_ok=True)  # ถ้ายังไม่มีโฟลเดอร์ก็สร้างขึ้นมา

    # เปิดไฟล์เพื่อเขียนรายงานลงไป
    with open(
        output_path,
        "w",  # ใช้โหมดเขียนไฟล์
        encoding="utf-8"  # ตั้งค่าให้รองรับภาษาไทย
    ) as file:

        file.write(report_text)  # เอารายงานทั้งหมดเขียนลงไฟล์

    return report_text  # ส่งข้อความรายงานกลับไป

# ส่วนนี้เอาไว้ลองทดสอบว่า MODULE 3 ทำงานได้ไหม
if __name__ == "__main__":

    # สร้างข้อมูลจำลองขึ้นมาไว้ลองทดสอบ
    simulation_paths = [
        [10000, 10500, 11000],
        [10000, 9500, 9000],
        [10000, 10800, 11500]
    ]

    initial_investment = 10000  # ตั้งเงินลงทุนเริ่มต้นไว้ที่ 10,000
    confidence_level = 0.95  # ตั้งระดับความเชื่อมั่นไว้ที่ 95%

    # ส่งข้อมูลไปคำนวณความเสี่ยง
    risk_results = calculate_risk(
        simulation_paths,
        initial_investment,
        confidence_level
    )

    print("\nผลการประเมินความเสี่ยง")  # แสดงหัวข้อก่อนโชว์ผลลัพธ์

    # ตั้งชื่อภาษาไทยให้กับผลลัพธ์แต่ละตัว
    thai_labels = {
        "average_final_value": "มูลค่าเงินลงทุนเฉลี่ยเมื่อสิ้นสุด",
        "best_final_value": "มูลค่าเงินลงทุนสูงสุด",
        "worst_final_value": "มูลค่าเงินลงทุนต่ำสุด",
        "probability_of_loss": "โอกาสที่จะขาดทุน",
        "var": "มูลค่าความเสี่ยง (VaR)",
        "average_mdd": "ค่าเฉลี่ยการลดลงสูงสุดของพอร์ต",
        "worst_mdd": "การลดลงสูงสุดของพอร์ต"
    }

    for key, value in risk_results.items():  # วนเอาผลลัพธ์ออกมาทีละตัว
        label = thai_labels.get(key, key)  # เปลี่ยนชื่อจากภาษาอังกฤษเป็นภาษาไทย
        print(f"{label}: {value}")  # แสดงชื่อกับค่าที่คำนวณได้

    # รวมข้อมูลทั้งหมดไว้เพื่อเอาไปสร้างรายงาน
    analysis = {
        "ticker": "DEMO",  # ตั้งชื่อหุ้นตัวอย่างไว้ทดสอบ
        "initial_investment": initial_investment,  # ใส่เงินลงทุนเริ่มต้น
        "trading_days": 2,  # กำหนดจำนวนวันซื้อขาย
        "simulations": len(simulation_paths),  # นับว่ามีการจำลองทั้งหมดกี่รอบ
        "confidence_level": confidence_level,  # ใส่ระดับความเชื่อมั่น
        **risk_results,  # เอาผลความเสี่ยงทั้งหมดมารวมไว้ตรงนี้
        "mean_daily_return": 0.001,  # ใส่ผลตอบแทนรายวันตัวอย่าง
        "annualized_volatility": 0.20  # ใส่ค่าความผันผวนต่อปีตัวอย่าง
    }

    # สร้างรายงานแล้วเซฟเป็นไฟล์ TXT
    report = generate_report(
        analysis,
        "reports/risk_report.txt"  # กำหนดชื่อไฟล์กับโฟลเดอร์ที่จะเก็บ
    )

    print("\nสร้างรายงานเรียบร้อยแล้ว")  # บอกว่าสร้างไฟล์เสร็จแล้ว
    print(report)  # แสดงรายงานทั้งหมดออกมาดู

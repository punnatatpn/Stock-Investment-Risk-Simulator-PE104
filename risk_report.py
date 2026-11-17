# QUANT - ระบบจำลองการลงทุนในหุ้น
# MODULE 3: การประเมินความเสี่ยงและรายงานการลงทุน
#
# หน้าที่หลัก:
# 1. นำข้อมูลจากการจำลองมาคำนวณความเสี่ยง
# 2. คำนวณโอกาสขาดทุน, VaR และ Maximum Drawdown
# 3. สร้างรายงานผลการลงทุนและบันทึกเป็นไฟล์ TXT

import statistics  # ใช้คำนวณค่าเฉลี่ย
import math        # ใช้คำนวณทางคณิตศาสตร์
import os          # ใช้จัดการไฟล์และโฟลเดอร์
from datetime import datetime  # ใช้ดึงวันที่และเวลาปัจจุบัน


# ฟังก์ชันที่ 1: หาค่าการลดลงสูงสุดของพอร์ต
def calculate_maximum_drawdown(path):
    """
    คำนวณว่ามูลค่าพอร์ตเคยลดลงจากจุดสูงสุดมากที่สุดกี่เปอร์เซ็นต์

    Args:
        path (list): รายการมูลค่าพอร์ตในแต่ละวัน

    Returns:
        float: ค่าการลดลงสูงสุดในรูปแบบทศนิยม
    """

    # ตรวจว่ามีข้อมูลส่งเข้ามาหรือไม่
    if not isinstance(path, (list, tuple)) or len(path) == 0:
        raise ValueError("เส้นทางการจำลองต้องมีข้อมูล")

    # ตรวจว่าข้อมูลทุกตัวเป็นตัวเลขที่ถูกต้องหรือไม่
    if not all(
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
        and value >= 0
        for value in path
    ):
        raise ValueError("มูลค่าพอร์ตต้องเป็นตัวเลขที่ถูกต้องและไม่ติดลบ")

    # กำหนดให้ค่าแรกเป็นจุดสูงสุดเริ่มต้น
    running_peak = path[0]

    # ตั้งค่าการลดลงสูงสุดเริ่มต้นเป็น 0
    maximum_drawdown = 0.0

    # ตรวจสอบมูลค่าพอร์ตทีละวัน
    for current_value in path:

        # ถ้ามูลค่าปัจจุบันสูงกว่าจุดสูงสุดเดิม
        # ให้เปลี่ยนเป็นจุดสูงสุดใหม่
        if current_value > running_peak:
            running_peak = current_value

        # คำนวณว่าพอร์ตลดลงจากจุดสูงสุดไปเท่าไร
        if running_peak > 0:
            drawdown = 1 - (current_value / running_peak)
        else:
            drawdown = 0.0

        # เก็บค่าการลดลงที่มากที่สุด
        if drawdown > maximum_drawdown:
            maximum_drawdown = drawdown

    return float(maximum_drawdown)


# ฟังก์ชันที่ 2: ใช้หาค่าเปอร์เซ็นไทล์
def calculate_percentile(sorted_values, confidence_level):
    """
    หาค่าเปอร์เซ็นไทล์จากข้อมูลที่เรียงจากน้อยไปมากแล้ว

    Args:
        sorted_values (list): รายการตัวเลขที่เรียงจากน้อยไปมาก
        confidence_level (float): ระดับเปอร์เซ็นไทล์ เช่น 0.95

    Returns:
        float: ค่าที่ได้จากการคำนวณเปอร์เซ็นไทล์
    """

    # ตรวจว่าข้อมูลเป็น list หรือ tuple
    if not isinstance(sorted_values, (list, tuple)):
        raise TypeError("ข้อมูลต้องเป็น list หรือ tuple")

    # ตรวจว่ามีข้อมูลหรือไม่
    if len(sorted_values) == 0:
        raise ValueError("ไม่พบข้อมูลสำหรับคำนวณเปอร์เซ็นไทล์")

    # ตรวจว่าข้อมูลทุกตัวเป็นตัวเลขที่ถูกต้อง
    if not all(
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
        for value in sorted_values
    ):
        raise ValueError("ข้อมูลต้องเป็นตัวเลขที่ถูกต้อง")

    # ตรวจว่าข้อมูลเรียงจากน้อยไปมากแล้วหรือไม่
    if list(sorted_values) != sorted(sorted_values):
        raise ValueError("ข้อมูลต้องเรียงจากน้อยไปมาก")

    # ตรวจระดับความเชื่อมั่น
    if (
        not isinstance(confidence_level, (int, float))
        or isinstance(confidence_level, bool)
        or not math.isfinite(confidence_level)
        or not 0 <= confidence_level <= 1
    ):
        raise ValueError("ระดับความเชื่อมั่นต้องอยู่ระหว่าง 0 ถึง 1")

    # นับจำนวนข้อมูลทั้งหมด
    n = len(sorted_values)

    # ถ้ามีข้อมูลเพียงตัวเดียว ให้คืนค่าตัวนั้น
    if n == 1:
        return float(sorted_values[0])

    # หาตำแหน่งของเปอร์เซ็นไทล์ที่ต้องการ
    position = (n - 1) * confidence_level

    # หาตำแหน่งด้านล่างและด้านบน
    lower_index = math.floor(position)
    upper_index = math.ceil(position)

    # ถ้าทั้งสองตำแหน่งเป็นตัวเดียวกัน
    # ก็ใช้ค่าจากตำแหน่งนั้นได้เลย
    if lower_index == upper_index:
        return float(sorted_values[lower_index])

    # หาระยะห่างระหว่างตำแหน่งที่ต้องการ
    fraction = position - lower_index

    # ดึงค่าตัวล่างและตัวบนออกมา
    lower_value = sorted_values[lower_index]
    upper_value = sorted_values[upper_index]

    # คำนวณค่าระหว่างตัวเลขทั้งสอง
    percentile = (
        lower_value + (upper_value - lower_value) * fraction
    )

    return float(percentile)


# ฟังก์ชันที่ 3: ใช้คำนวณความเสี่ยงในการลงทุน
def calculate_risk(
    simulation_paths,
    initial_investment,
    confidence_level
):
    """
    คำนวณความเสี่ยงและผลลัพธ์จากเส้นทางการจำลองทั้งหมด

    Args:
        simulation_paths (list): ผลการจำลองพอร์ตทั้งหมด
        initial_investment (float): เงินลงทุนเริ่มต้น
        confidence_level (float): ระดับความเชื่อมั่น เช่น 0.95

    Returns:
        dict: ผลการประเมินความเสี่ยงและมูลค่าพอร์ต
    """

    # ตรวจว่ามีข้อมูลการจำลองหรือไม่
    if not isinstance(simulation_paths, (list, tuple)):
        raise TypeError("ข้อมูลการจำลองต้องเป็น list หรือ tuple")

    if len(simulation_paths) == 0:
        raise ValueError("ไม่พบข้อมูลเส้นทางการจำลอง")

    # ตรวจเงินลงทุนเริ่มต้น
    if (
        not isinstance(initial_investment, (int, float))
        or isinstance(initial_investment, bool)
        or not math.isfinite(initial_investment)
        or initial_investment <= 0
    ):
        raise ValueError("เงินลงทุนเริ่มต้นต้องเป็นตัวเลขที่มากกว่า 0")

    # ตรวจระดับความเชื่อมั่น
    if (
        not isinstance(confidence_level, (int, float))
        or isinstance(confidence_level, bool)
        or not math.isfinite(confidence_level)
        or not 0 <= confidence_level <= 1
    ):
        raise ValueError("ระดับความเชื่อมั่นต้องอยู่ระหว่าง 0 ถึง 1")

    # ตรวจสอบข้อมูลการจำลองแต่ละรอบ
    for path in simulation_paths:

        if not isinstance(path, (list, tuple)) or len(path) == 0:
            raise ValueError("เส้นทางการจำลองต้องไม่เป็นค่าว่าง")

        for value in path:

            if (
                not isinstance(value, (int, float))
                or isinstance(value, bool)
            ):
                raise TypeError("ค่าภายในเส้นทางการจำลองต้องเป็นตัวเลข")

            if not math.isfinite(value) or value < 0:
                raise ValueError(
                    "มูลค่าพอร์ตต้องเป็นตัวเลขที่ถูกต้องและไม่ติดลบ"
                )

    # 1. หามูลค่าเงินลงทุนตอนจบของแต่ละรอบ
    final_values = [
        path[-1]
        for path in simulation_paths
    ]

    # หาค่าเฉลี่ย ค่าสูงสุด และค่าต่ำสุด
    average_final_value = statistics.mean(final_values)
    best_final_value = max(final_values)
    worst_final_value = min(final_values)

    # 2. หาว่ามีกี่รอบที่ขาดทุน
    loss_count = sum(
        1
        for value in final_values
        if value < initial_investment
    )

    # คำนวณสัดส่วนของรอบที่ขาดทุน
    probability_of_loss = loss_count / len(final_values)

    # 3. คำนวณค่าความเสี่ยง VaR
    losses = [
        initial_investment - value
        for value in final_values
    ]

    # เรียงผลขาดทุนจากน้อยไปมาก
    losses.sort()

    # หาค่า VaR ตามระดับความเชื่อมั่นที่กำหนด
    var_value = calculate_percentile(
        losses,
        confidence_level
    )

    # 4. คำนวณ Maximum Drawdown ของแต่ละรอบ
    maximum_drawdowns = [
        calculate_maximum_drawdown(path)
        for path in simulation_paths
    ]

    # หาค่าเฉลี่ย MDD และค่า MDD ที่มากที่สุด
    average_mdd = statistics.mean(maximum_drawdowns)
    worst_mdd = max(maximum_drawdowns)

    # 5. รวมผลลัพธ์ทั้งหมดไว้ใน Dictionary
    risk_results = {
        "average_final_value": float(average_final_value),
        "best_final_value": float(best_final_value),
        "worst_final_value": float(worst_final_value),
        "probability_of_loss": float(probability_of_loss),
        "var": float(var_value),
        "average_mdd": float(average_mdd),
        "worst_mdd": float(worst_mdd)
    }

    return risk_results


# ฟังก์ชันที่ 4: สร้างรายงานผลการลงทุน
def generate_report(analysis, output_path):
    """
    สร้างรายงานผลการลงทุนและบันทึกเป็นไฟล์ TXT

    Args:
        analysis (dict): ข้อมูลผลการวิเคราะห์ทั้งหมด
        output_path (str): ตำแหน่งที่จะบันทึกไฟล์รายงาน

    Returns:
        str: ข้อความรายงานทั้งหมด
    """

    # ตรวจว่าข้อมูลที่รับมาเป็น Dictionary หรือไม่
    if not isinstance(analysis, dict):
        raise TypeError("ข้อมูลสำหรับสร้างรายงานต้องเป็น Dictionary")

    # ตรวจตำแหน่งบันทึกไฟล์
    if not isinstance(output_path, str) or not output_path.strip():
        raise ValueError("กรุณาระบุตำแหน่งบันทึกไฟล์")

    # รายการข้อมูลที่จำเป็นต้องใช้ในรายงาน
    required_keys = [
        "ticker",
        "initial_investment",
        "trading_days",
        "simulations",
        "confidence_level",
        "average_final_value",
        "best_final_value",
        "worst_final_value",
        "probability_of_loss",
        "var",
        "average_mdd",
        "worst_mdd"
    ]

    # ตรวจว่าข้อมูลที่จำเป็นมีครบหรือไม่
    for key in required_keys:

        if key not in analysis:
            raise KeyError(
                f"ไม่พบข้อมูลที่จำเป็นในรายงาน: {key}"
            )

    # ตรวจข้อมูลตัวเลขที่ต้องใช้ในรายงาน
    numeric_keys = [
        "initial_investment",
        "confidence_level",
        "average_final_value",
        "best_final_value",
        "worst_final_value",
        "probability_of_loss",
        "var",
        "average_mdd",
        "worst_mdd"
    ]

    for key in numeric_keys:
        value = analysis[key]

        if (
            not isinstance(value, (int, float))
            or isinstance(value, bool)
            or not math.isfinite(value)
        ):
            raise ValueError(f"ข้อมูล {key} ต้องเป็นตัวเลขที่ถูกต้อง")

    # ตรวจชื่อหุ้น
    if not isinstance(analysis["ticker"], str) or not analysis["ticker"].strip():
        raise ValueError("ชื่อหุ้นไม่ถูกต้อง")

    # ตรวจจำนวนวันซื้อขายและจำนวนครั้งที่จำลอง
    for key in ["trading_days", "simulations"]:
        value = analysis[key]

        if (
            not isinstance(value, int)
            or isinstance(value, bool)
            or value <= 0
        ):
            raise ValueError(f"{key} ต้องเป็นจำนวนเต็มที่มากกว่า 0")

    # ตรวจค่าพื้นฐานก่อนสร้างรายงาน
    if analysis["initial_investment"] <= 0:
        raise ValueError("เงินลงทุนเริ่มต้นต้องมากกว่า 0")

    if not 0 <= analysis["confidence_level"] <= 1:
        raise ValueError("ระดับความเชื่อมั่นต้องอยู่ระหว่าง 0 ถึง 1")

    if not 0 <= analysis["probability_of_loss"] <= 1:
        raise ValueError("โอกาสขาดทุนต้องอยู่ระหว่าง 0 ถึง 1")

    if not 0 <= analysis["average_mdd"] <= 1:
        raise ValueError("ค่า Average MDD ไม่ถูกต้อง")

    if not 0 <= analysis["worst_mdd"] <= 1:
        raise ValueError("ค่า Worst MDD ไม่ถูกต้อง")

    # ดึงข้อมูลเพิ่มเติม ถ้ามีส่งมาจากการวิเคราะห์
    mean_daily_return = analysis.get("mean_daily_return")
    annualized_volatility = analysis.get("annualized_volatility")

    # ตรวจข้อมูลเพิ่มเติมก่อนนำไปแสดง
    for key, value in [
        ("mean_daily_return", mean_daily_return),
        ("annualized_volatility", annualized_volatility)
    ]:
        if value is not None:
            if (
                not isinstance(value, (int, float))
                or isinstance(value, bool)
                or not math.isfinite(value)
            ):
                raise ValueError(f"ข้อมูล {key} ไม่ถูกต้อง")

    # เริ่มสร้างข้อความรายงาน
    report_lines = [
        "=" * 60,
        "QUANT - ระบบจำลองการลงทุนในหุ้น",
        "รายงานการประเมินความเสี่ยงและผลการลงทุน",
        "=" * 60,
        f"วันที่จัดทำรายงาน: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",

        "",
        "ข้อมูลหุ้น",
        "-" * 60,
        f"ชื่อย่อหุ้น: {analysis['ticker']}",

        "",
        "การตั้งค่าการจำลอง",
        "-" * 60,
        f"เงินลงทุนเริ่มต้น: {analysis['initial_investment']:,.2f}",
        f"จำนวนวันซื้อขาย: {analysis['trading_days']}",
        f"จำนวนครั้งในการจำลอง: {analysis['simulations']}",
        f"ระดับความเชื่อมั่น: {analysis['confidence_level'] * 100:.2f}%",

        "",
        "ผลการลงทุน",
        "-" * 60,
        f"มูลค่าเงินลงทุนเฉลี่ยเมื่อสิ้นสุด: {analysis['average_final_value']:,.2f}",
        f"มูลค่าเงินลงทุนสูงสุด: {analysis['best_final_value']:,.2f}",
        f"มูลค่าเงินลงทุนต่ำสุด: {analysis['worst_final_value']:,.2f}",

        "",
        "การประเมินความเสี่ยง",
        "-" * 60,
        f"โอกาสที่จะขาดทุน: {analysis['probability_of_loss'] * 100:.2f}%",
        f"มูลค่าความเสี่ยง (VaR): {analysis['var']:,.2f}",
        f"ค่าเฉลี่ยการลดลงสูงสุดของพอร์ต (MDD): {analysis['average_mdd'] * 100:.2f}%",
        f"การลดลงสูงสุดของพอร์ต: {analysis['worst_mdd'] * 100:.2f}%"
    ]

    # ถ้ามีผลตอบแทนเฉลี่ยรายวัน ให้เพิ่มลงในรายงาน
    if mean_daily_return is not None:
        report_lines.append(
            f"ผลตอบแทนเฉลี่ยรายวัน: {mean_daily_return * 100:.4f}%"
        )

    # ถ้ามีค่าความผันผวนต่อปี ให้เพิ่มลงในรายงาน
    if annualized_volatility is not None:
        report_lines.append(
            f"ความผันผวนต่อปี: {annualized_volatility * 100:.2f}%"
        )

    # เพิ่มคำอธิบายท้ายรายงาน
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

    # นำข้อความแต่ละบรรทัดมาต่อกันเป็นรายงานเดียว
    report_text = "\n".join(report_lines)

    # หาตำแหน่งโฟลเดอร์ที่จะบันทึกรายงาน
    directory = os.path.dirname(
        os.path.abspath(output_path)
    )

    # ถ้าโฟลเดอร์ยังไม่มี ให้สร้างขึ้นมา
    os.makedirs(directory, exist_ok=True)

    # เปิดไฟล์และบันทึกรายงาน โดยใช้ UTF-8 เพื่อรองรับภาษาไทย
    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(report_text)

    # ส่งข้อความรายงานกลับไปให้ส่วนอื่นใช้งาน
    return report_text


# ส่วนนี้ใช้ทดสอบ MODULE 3 แยกจากโปรแกรมหลัก
if __name__ == "__main__":

    # สร้างข้อมูลจำลองตัวอย่าง 3 รอบ
    simulation_paths = [
        [10000, 10500, 11000],
        [10000, 9500, 9000],
        [10000, 10800, 11500]
    ]

    # กำหนดเงินลงทุนเริ่มต้น
    initial_investment = 10000

    # กำหนดระดับความเชื่อมั่น 95%
    confidence_level = 0.95

    # ส่งข้อมูลไปคำนวณความเสี่ยง
    risk_results = calculate_risk(
        simulation_paths,
        initial_investment,
        confidence_level
    )

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

    # แสดงผลการประเมินความเสี่ยง
    print("\nผลการประเมินความเสี่ยง")

    for key, value in risk_results.items():
        label = thai_labels.get(key, key)
        print(f"{label}: {value}")

    # รวมข้อมูลทั้งหมดเพื่อใช้สร้างรายงานตัวอย่าง
    analysis = {
        "ticker": "DEMO",
        "initial_investment": initial_investment,
        "trading_days": 2,
        "simulations": len(simulation_paths),
        "confidence_level": confidence_level,
        **risk_results,
        "mean_daily_return": 0.001,
        "annualized_volatility": 0.20
    }

    # สร้างรายงานตัวอย่างแยกจากรายงานหลัก
    report = generate_report(
        analysis,
        "reports/demo_risk_report.txt"
    )

    print("\nสร้างรายงานตัวอย่างเรียบร้อยแล้ว")
    print(report)

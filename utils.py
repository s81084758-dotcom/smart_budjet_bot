import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import os

def create_report_chart(data, user_id):
    if not data: return None
    labels = [f"{row[0]} {row[1]}" for row in data]
    sizes = [row[2] for row in data]
    
    plt.figure(figsize=(8, 6))
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
    plt.title("Oylik Xarajatlar Analizi")
    
    path = f"report_{user_id}.png"
    plt.savefig(path)
    plt.close()
    return path




def get_usd_rate():
    # vaqtincha fixed kurs (keyin API qo‘shsa ham bo‘ladi)
    return 12500  # 1 USD = 12500 UZS


def convert_currency(amount, from_cur, to_cur):
    rate = get_usd_rate()

    if from_cur == to_cur:
        return amount

    if from_cur == "UZS" and to_cur == "USD":
        return amount / rate

    if from_cur == "USD" and to_cur == "UZS":
        return amount * rate

    return amount
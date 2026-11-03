"""Учёт личных расходов с анализом по категориям и контролем лимитов.

Режимы запуска:
    python expenses.py                      - интерактивный ввод расходов
    python expenses.py --auto 8 --seed 1    - автоматическая демонстрация
"""
import argparse
import random
from datetime import datetime

CATEGORIES = ["еда", "транспорт", "жильё", "развлечения", "здоровье"]
LIMITS = {"еда": 15000, "транспорт": 4000, "жильё": 20000,
          "развлечения": 5000, "здоровье": 3000}   # месячные лимиты, руб.
MIN_SUM = 1
MAX_SUM = 100000


def limit_of(category):
    """Месячный лимит расходов по категории."""
    return LIMITS[category]


def check_expense(category, amount, balance):
    """Проверка записи о расходе. Возвращает текст ошибки или None."""
    if category not in CATEGORIES:
        return "Неизвестная категория: " + ", ".join(CATEGORIES)
    if amount < MIN_SUM or amount > MAX_SUM:
        return f"Сумма должна быть от {MIN_SUM} до {MAX_SUM}"
    if amount > balance:
        return "Расход больше остатка на счёте"
    return None


def total_by_category(history):
    """Суммы расходов по каждой категории."""
    totals = {c: 0 for c in CATEGORIES}
    for item in history:
        totals[item["category"]] += item["amount"]
    return totals


def find_overruns(totals):
    """Категории с превышением лимита: {категория: превышение}."""
    over = {}
    for category, spent in totals.items():
        if spent > limit_of(category):
            over[category] = spent - limit_of(category)
    return over


def format_money(x):
    """Денежный формат: два знака после запятой и суффикс 'р'."""
    return f"{x:,.2f}".replace(",", " ").replace(".", ",") + "р"


def make_report(user, start, balance, history, finished):
    """Итоговый отчёт о расходах в виде списка строк."""
    totals = total_by_category(history)
    overruns = find_overruns(totals)
    lines = [
        "=== ОТЧЕТ О РАСХОДАХ ===",
        f"Пользователь: {user}",
        f"Записей: {len(history)}",
    ]
    for category in CATEGORIES:
        lines.append(f"  {category}: {format_money(totals[category])}")
    if overruns:
        for category, over in overruns.items():
            lines.append(f"Превышен лимит ({category}): "
                         f"{format_money(over)}")
    else:
        lines.append("Превышений лимитов нет")
    lines += [
        f"Баланс в начале: {format_money(start)}",
        f"ИТОГО: {format_money(balance)}",
        f"Время завершения: {finished:%d.%m.%Y %H:%M}",
    ]
    return lines


def process_expense(balance, category, amount, history):
    """Одна запись: проверка, учёт, пересчёт. Возвращает новый баланс."""
    error = check_expense(category, amount, balance)
    if error:
        print("Ошибка:", error)
        return balance
    history.append({"category": category, "amount": amount})
    balance -= amount
    print(f"Расход: {category}, {format_money(amount)}. "
          f"Остаток: {format_money(balance)}")
    return balance


def auto_mode(rng, start, count):
    """Автоматический режим: случайные расходы по категориям."""
    balance, history = start, []
    for _ in range(count):
        if balance < MIN_SUM:
            print("Средств недостаточно, ввод остановлен")
            break
        category = rng.choice(CATEGORIES)
        amount = rng.choice([300, 800, 1500, 2500, 4000])
        balance = process_expense(balance, category, amount, history)
    return balance, history


def interactive_mode(start):
    """Интерактивный режим: ввод расходов с клавиатуры."""
    balance, history = start, []
    names = ", ".join(CATEGORIES)
    print(f"Остаток: {format_money(balance)}. Категории: {names}")
    while balance >= MIN_SUM:
        category = input("Категория (или q для выхода): ").strip().lower()
        if category == "q":
            break
        try:
            amount = int(input("Сумма расхода: "))
        except ValueError:
            print("Ошибка: нужно ввести целое число")
            continue
        balance = process_expense(balance, category, amount, history)
    return balance, history


def main():
    parser = argparse.ArgumentParser(description="Учёт личных расходов")
    parser.add_argument("--auto", type=int, metavar="N",
                        help="сгенерировать N расходов")
    parser.add_argument("--seed", type=int,
                        help="начальное значение генератора")
    parser.add_argument("--balance", type=int, default=50000,
                        help="начальный баланс")
    parser.add_argument("--name", default="Константин",
                        help="имя пользователя")
    args = parser.parse_args()

    if args.auto:
        rng = random.Random(args.seed)
        balance, history = auto_mode(rng, args.balance, args.auto)
    else:
        balance, history = interactive_mode(args.balance)
    print()
    report = make_report(args.name, args.balance, balance, history,
                         datetime.now())
    for line in report:
        print(line)


if __name__ == "__main__":
    main()

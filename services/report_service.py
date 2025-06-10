import csv
from datetime import datetime, date, timedelta
from io import BytesIO, StringIO
from collections import defaultdict, OrderedDict

import matplotlib.pyplot as plt
from aiogram.types import BufferedInputFile

from models.transaction import get_transactions
from models.user import get_budget

def build_monthly_diagrams(user_id: int) -> tuple[BufferedInputFile, BufferedInputFile]:
    today = datetime.now()
    month_start = today.replace(day=1).strftime("%Y-%m-%d")
    rows = get_transactions(user_id, month_start, today.strftime("%Y-%m-%d"))

    exp_sum = 0.0
    inc_sum = 0.0
    by_cat: dict[str, float] = {}
    for r in rows:
        amt = r["amount"]
        cat = r["category"].strip().title()
        if r["type"] == "expense":
            by_cat[cat] = by_cat.get(cat, 0) + amt
            exp_sum += amt
        else:
            inc_sum += amt

    plt.style.use("seaborn-v0_8-pastel")

    fig1, ax1 = plt.subplots(figsize=(6, 6), dpi=150)
    if by_cat:
        labels = list(by_cat.keys())
        values = list(by_cat.values())

        colors = plt.cm.Pastel1.colors[: len(labels)]

        wedges, texts, autotexts = ax1.pie( values, labels=labels, autopct="%1.1f%%", pctdistance=0.75,
            labeldistance=1.05, colors=colors, wedgeprops={"edgecolor": "white", "linewidth": 1.0},
            textprops={"color": "#333333", "fontsize": 10}, startangle=90,
        )

        ax1.legend(wedges, labels, title="Категории", loc="center left", bbox_to_anchor=(1.0, 0.5), fontsize=9, title_fontsize=11,)
    else:
        ax1.text( 0.5, 0.5, "Нет расходов",
            ha="center", va="center", fontsize=12, color="#555555",
        )

    ax1.set_title(
        "Расходы по категориям за месяц",
        fontsize=14,
        fontweight="bold",
        pad=20,
    )
    ax1.axis("equal")
    plt.tight_layout()

    buf1 = BytesIO()
    fig1.savefig(buf1, format="png", transparent=True)
    buf1.seek(0)
    plt.close(fig1)
    file1 = BufferedInputFile(buf1.getvalue(), filename="expense_pie.png")

    fig2, ax2 = plt.subplots(figsize=(6, 4), dpi=150)
    categories = ["Расходы", "Доходы"]
    values2 = [exp_sum, inc_sum]

    bar_colors = [plt.cm.Set2.colors[0], plt.cm.Set2.colors[1]]

    bars = ax2.bar(
        categories,
        values2,
        color=bar_colors,
        edgecolor="white",
        linewidth=1.2,
        width=0.6,
    )

    max_val = max(exp_sum, inc_sum, 1)
    for bar in bars:
        height = bar.get_height()
        ax2.text(
            bar.get_x() + bar.get_width() / 2,
            height + max_val * 0.02,
            f"{height:.0f}",
            ha="center",
            va="bottom",
            fontsize=11,
            color="#333333",
        )

    ax2.set_title(
        "Доходы vs Расходы за месяц",
        fontsize=14,
        fontweight="bold",
        pad=15,
    )
    ax2.set_ylabel("Сумма (₽)", fontsize=12)
    ax2.set_ylim(0, max_val * 1.15)
    ax2.grid(axis="y", linestyle="--", linewidth=0.5, alpha=0.7)

    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)

    ax2.spines["left"].set_color("#555555")
    ax2.spines["bottom"].set_color("#555555")

    plt.tight_layout()

    buf2 = BytesIO()
    fig2.savefig(buf2, format="png", transparent=True)
    buf2.seek(0)
    plt.close(fig2)
    file2 = BufferedInputFile(buf2.getvalue(), filename="inc_exp_bar.png")

    return file1, file2

def build_top_comments(user_id: int) -> str:
    today = date.today()
    start = today.replace(day=1).strftime("%Y-%m-%d")
    rows = get_transactions(user_id, start, today.strftime("%Y-%m-%d"))

    sums: dict[str, float] = {}
    for r in rows:
        comment = (r["comment"] or "").strip()
        if not comment:
            continue
        key = comment.lower()
        sums[key] = sums.get(key, 0) + r["amount"]

    if not sums:
        return "Нет транзакций с комментариями за месяц."

    top5 = sorted(sums.items(), key=lambda kv: kv[1], reverse=True)[:5]
    lines = ["📋 Топ-5 по комментариям за месяц:"]
    for key, total in top5:
        label = key.title()
        lines.append(f"  • {label}: {total:.2f}")
    return "\n".join(lines)

def build_csv_report(user_id: int) -> BufferedInputFile:
    today = date.today()
    start = today.replace(day=1).strftime("%Y-%m-%d")
    end = today.strftime("%Y-%m-%d")
    rows = get_transactions(user_id, start, end)

    buf = StringIO()
    writer = csv.writer(buf, delimiter=';', lineterminator='\n')
    writer.writerow(["Дата", "Тип", "Категория", "Сумма", "Комментарий"])
    for r in rows:
        writer.writerow([
            r["date"],
            r["type"],
            r["category"],
            f"{r['amount']:.2f}",
            r["comment"] or ""
        ])

    data = buf.getvalue().encode("utf-8-sig")
    bio = BytesIO(data)
    bio.name = f"report_{start}_to_{end}.csv"
    return BufferedInputFile(bio.read(), filename=bio.name)

def build_common_report(user_id: int, period: str, start: str | None = None, end: str | None = None) -> str:
    if period == "day":
        today_str = date.today().strftime("%Y-%m-%d")
        start = end = today_str
    elif period == "month":
        today = date.today()
        start = today.replace(day=1).strftime("%Y-%m-%d")
        end = today.strftime("%Y-%m-%d")
    elif period == "custom":
        pass
    else:
        return "Неверный период."

    rows = get_transactions(user_id, start, end)

    exp_by: dict[str, float] = {}
    inc_by: dict[str, float] = {}
    total_exp = total_inc = 0.0

    for r in rows:
        amt = r["amount"]
        cat = r["category"].strip().title()
        if r["type"] == "expense":
            exp_by[cat] = exp_by.get(cat, 0) + amt
            total_exp += amt
        else:
            inc_by[cat] = inc_by.get(cat, 0) + amt
            total_inc += amt

    header_map = {"day": "за день", "month": "за месяц", "custom": "за период"}
    header = header_map.get(period, "за период")
    lines = [f"📋 Отчёт {header} ({start} — {end}):", ""]

    lines.append(f"💸 Всего расходов: {total_exp:.2f}")
    for cat, s in sorted(exp_by.items(), key=lambda kv: kv[1], reverse=True):
        lines.append(f"  • {cat}: {s:.2f}")
    lines.append("")

    lines.append(f"💵 Всего доходов: {total_inc:.2f}")
    for cat, s in sorted(inc_by.items(), key=lambda kv: kv[1], reverse=True):
        lines.append(f"  • {cat}: {s:.2f}")

    budget = get_budget(user_id)
    if budget and budget > 0:
        month_start = date.today().replace(day=1).strftime("%Y-%m-%d")
        month_rows = get_transactions(user_id, month_start, date.today().strftime("%Y-%m-%d"))
        total_month_exp = sum(r["amount"] for r in month_rows if r["type"] == "expense")
        remaining = budget - total_month_exp

        lines.append("")
        lines.append(f"Бюджет на месяц: {budget:.2f}")
        if remaining < 0:
            lines.append(f"❗️ Вы вышли за пределы бюджета на {abs(remaining):.2f}")
        else:
            warn = " ⚠️ мало осталось!" if remaining < budget * 0.1 else ""
            lines.append(f"Осталось: {remaining:.2f}{warn}")

    return "\n".join(lines)

def build_spending_trends(user_id: int) -> tuple[BufferedInputFile, BufferedInputFile, str]:
    today = date.today()
    month_start = today.replace(day=1)
    month_end = today

    prev_month_last_day = month_start - timedelta(days=1)
    prev_month_start = prev_month_last_day.replace(day=1)
    prev_month_end = prev_month_last_day

    curr_rows = get_transactions(
        user_id,
        month_start.strftime("%Y-%m-%d"),
        month_end.strftime("%Y-%m-%d")
    )
    prev_rows = get_transactions(
        user_id,
        prev_month_start.strftime("%Y-%m-%d"),
        prev_month_end.strftime("%Y-%m-%d")
    )

    curr_spend_by_day = OrderedDict()
    prev_spend_by_day = OrderedDict()

    day_iter = month_start
    while day_iter <= month_end:
        curr_spend_by_day[day_iter] = 0.0
        day_iter += timedelta(days=1)

    day_iter = prev_month_start
    while day_iter <= prev_month_end:
        prev_spend_by_day[day_iter] = 0.0
        day_iter += timedelta(days=1)

    for r in curr_rows:
        if r["type"] == "expense":
            d = date.fromisoformat(r["date"])
            if d in curr_spend_by_day:
                curr_spend_by_day[d] += r["amount"]

    for r in prev_rows:
        if r["type"] == "expense":
            d = date.fromisoformat(r["date"])
            if d in prev_spend_by_day:
                prev_spend_by_day[d] += r["amount"]

    plt.style.use("seaborn-v0_8-pastel")
    fig1, ax1 = plt.subplots(figsize=(7, 4), dpi=150)

    x_curr = list(curr_spend_by_day.keys())
    y_curr = list(curr_spend_by_day.values())

    bars = ax1.bar(
        [d.day for d in x_curr],
        y_curr,
        color=plt.cm.Set2.colors[: len(x_curr)],
        edgecolor="gray",
        linewidth=0.5,
        width=0.7
    )

    max_val = max(y_curr + [1])
    for bar in bars:
        height = bar.get_height()
        if height > 0:
            ax1.text(
                bar.get_x() + bar.get_width() / 2,
                height + max_val * 0.02,
                f"{height:.0f}",
                ha="center",
                va="bottom",
                fontsize=9,
                color="#333333"
            )

    ax1.set_title(
        "Динамика трат по дням (текущий месяц)",
        fontsize=14,
        fontweight="bold",
        pad=10
    )
    ax1.set_xlabel("День месяца", fontsize=11)
    ax1.set_ylabel("Сумма расходов (₽)", fontsize=11)
    ax1.set_xticks([d.day for d in x_curr])
    ax1.set_xticklabels([str(d.day) for d in x_curr], rotation=45, fontsize=9)
    ax1.grid(axis="y", linestyle="--", linewidth=0.5, alpha=0.7)

    plt.tight_layout()
    buf_month = BytesIO()
    fig1.savefig(buf_month, format="png", transparent=True)
    buf_month.seek(0)
    plt.close(fig1)
    file_month_bar = BufferedInputFile(buf_month.getvalue(), filename="spend_trend_month_bar.png")


    last6 = []
    cursor = month_start
    for i in range(6):
        first_day = (cursor.replace(day=1) - timedelta(days=0)).replace(day=1)
        last6.append(first_day)
        cursor = first_day - timedelta(days=1)

    last6 = list(reversed(last6))

    def month_last_day(dt: date) -> date:
        nxt = (dt.replace(day=28) + timedelta(days=4))
        return nxt.replace(day=1) - timedelta(days=1)

    months_labels = []
    months_sums = []

    for m_start in last6:
        m_end = month_last_day(m_start)
        if m_start == month_start:
            m_end = month_end

        rows = get_transactions(
            user_id,
            m_start.strftime("%Y-%m-%d"),
            m_end.strftime("%Y-%m-%d")
        )
        total = sum(r["amount"] for r in rows if r["type"] == "expense")
        months_sums.append(total)
        months_labels.append(m_start.strftime("%b %Y"))

    fig2, ax2 = plt.subplots(figsize=(7, 4), dpi=150)

    bars = ax2.bar(
        months_labels,
        months_sums,
        color=plt.cm.Pastel1.colors[: len(months_labels)],
        edgecolor="gray",
        linewidth=0.5,
        width=0.6
    )

    max_month_val = max(months_sums + [1])
    for bar in bars:
        h = bar.get_height()
        if h > 0:
            ax2.text(
                bar.get_x() + bar.get_width() / 2,
                h + max_month_val * 0.02,
                f"{h:.0f}",
                ha="center",
                va="bottom",
                fontsize=9,
                color="#333333"
            )

    ax2.set_title(
        "Траты за последние 6 месяцев",
        fontsize=14,
        fontweight="bold",
        pad=10
    )
    ax2.set_ylabel("Сумма расходов (₽)", fontsize=11)
    ax2.set_xlabel("Месяц", fontsize=11)
    ax2.tick_params(axis="x", rotation=45, labelsize=9)
    ax2.grid(axis="y", linestyle="--", linewidth=0.5, alpha=0.7)

    plt.tight_layout()
    buf_6months = BytesIO()
    fig2.savefig(buf_6months, format="png", transparent=True)
    buf_6months.seek(0)
    plt.close(fig2)
    file_last6_bar = BufferedInputFile(buf_6months.getvalue(), filename="spend_trend_last6months_bar.png")

    total_curr_month = sum(curr_spend_by_day.values())
    total_prev_month = sum(prev_spend_by_day.values())
    if total_prev_month > 0:
        change = (total_curr_month - total_prev_month) / total_prev_month * 100
    else:
        change = 0.0

    if total_prev_month == 0 and total_curr_month == 0:
        analysis_text = "Нет данных по расходам за текущий и предыдущий месяцы."
    elif total_prev_month == 0 and total_curr_month > 0:
        analysis_text = "В прошлом месяце у вас не было расходов, а в этом месяце они есть."
    else:
        change_abs = abs(change)
        if change > 0:
            analysis_text = (
                f"🔍 В этом месяце вы потратили {total_curr_month:.2f}₽ — "
                f"на {change_abs:.1f}% больше, чем в прошлом месяце ({total_prev_month:.2f}₽)."
            )
        elif change < 0:
            analysis_text = (
                f"🔍 В этом месяце вы потратили {total_curr_month:.2f}₽ — "
                f"на {change_abs:.1f}% меньше, чем в прошлом месяце ({total_prev_month:.2f}₽)."
            )
        else:
            analysis_text = (
                f"🔍 В этом месяце расходы ({total_curr_month:.2f}₽) совпадают с расходами "
                f"прошлого месяца ({total_prev_month:.2f}₽)."
            )

    return file_month_bar, file_last6_bar, analysis_text
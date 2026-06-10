import streamlit as st
import pandas as pd
import datetime
from dateutil.relativedelta import relativedelta

# Настройка страницы
st.set_page_config(
    page_title="Интерактивный кредитный калькулятор",
    page_icon="💰",
    layout="wide"
)

# Заголовок приложения
st.title("💰 Интерактивный кредитный калькулятор")
st.write("Приложение рассчитывает график платежей для аннуитетного и дифференцированного типов кредита.")

# Инициализация sidebar для ввода данных
st.sidebar.header("📋 Входные данные")

# 1. Сумма кредита
credit_amount = st.sidebar.number_input(
    "Сумма кредита (руб.):",
    min_value=0.0,
    value=100000.0,
    step=1000.0,
    format="%.2f"
)

# 2. Процентная ставка
interest_rate = st.sidebar.number_input(
    "Годовая процентная ставка (%):",
    min_value=0.0,
    value=12.0,
    step=0.1,
    format="%.2f"
)

# 3. Срок кредита
loan_term = st.sidebar.number_input(
    "Срок кредита (в месяцах):",
    min_value=0,
    value=12,
    step=1
)

# 4. Тип платежа
payment_type = st.sidebar.selectbox(
    "Тип платежа:",
    options=["Аннуитетный", "Дифференцированный"]
)

# 5. Дата первого платежа
first_payment_date = st.sidebar.date_input(
    "Дата первого платежа:",
    value=datetime.date.today()
)

# Кнопка для запуска расчета
calculate_button = st.sidebar.button("Рассчитать кредит", type="primary")

# Валидация входных данных / Защита от ошибок
if calculate_button:
    if credit_amount <= 0:
        st.error("❌ Ошибка: Сумма кредита должна быть больше нуля.")
        st.stop()  # Условный рендеринг: остановка выполнения

    if interest_rate <= 0:
        st.error("❌ Ошибка: Процентная ставка должна быть больше нуля.")
        st.stop()

    if loan_term <= 0:
        st.error("❌ Ошибка: Срок кредита должен быть не менее 1 месяца.")
        st.stop()

    # Логика расчетов
    # Месячная процентная ставка
    monthly_rate = (interest_rate / 100) / 12

    # Списки для сбора данных графика платежей
    dates = []
    start_balances = []
    payments = []
    interest_parts = []
    principal_parts = []
    end_balances = []

    current_balance = credit_amount
    current_date = first_payment_date

    # Расчет для АННУИТЕТНОГО платежа
    if payment_type == "Аннуитетный":
        # Формула аннуитетного платежа: A = Капитал * (p * (1 + p)^n) / ((1 + p)^n - 1)
        if monthly_rate == 0:
            annuity_payment = credit_amount / loan_term
        else:
            annuity_payment = credit_amount * (monthly_rate * (1 + monthly_rate) ** loan_term) / ((1 + monthly_rate) ** loan_term - 1)

        for month in range(1, loan_term + 1):
            # Процентная часть
            interest_part = current_balance * monthly_rate
            # Долговая часть (тело кредита)
            principal_part = annuity_payment - interest_part

            # Корректировка для последнего месяца, чтобы избежать копеечных погрешностей округления
            if month == loan_term:
                principal_part = current_balance
                annuity_payment = principal_part + interest_part

            end_balance = current_balance - principal_part
            if end_balance < 0:
                end_balance = 0.0

            # Сохраняем значения
            dates.append(current_date.strftime("%d.%m.%Y"))
            start_balances.append(round(current_balance, 2))
            payments.append(round(annuity_payment, 2))
            interest_parts.append(round(interest_part, 2))
            principal_parts.append(round(principal_part, 2))
            end_balances.append(round(end_balance, 2))

            # Переход к следующему периоду
            current_balance = end_balance
            current_date += relativedelta(months=1)

    # Расчет для ДИФФЕРЕНЦИРОВАННОГО платежа
    elif payment_type == "Дифференцированный":
        # Постоянная часть основного долга каждый месяц
        constant_principal = credit_amount / loan_term

        for month in range(1, loan_term + 1):
            # Процентная часть на остаток долга
            interest_part = current_balance * monthly_rate
            # В дифференцированном типе основной долг фиксирован
            principal_part = constant_principal

            # Корректировка последнего месяца
            if month == loan_term:
                principal_part = current_balance

            # Общий ежемесячный платеж
            diff_payment = principal_part + interest_part
            end_balance = current_balance - principal_part

            if end_balance < 0:
                end_balance = 0.0

            # Сохраняем значения
            dates.append(current_date.strftime("%d.%m.%Y"))
            start_balances.append(round(current_balance, 2))
            payments.append(round(diff_payment, 2))
            interest_parts.append(round(interest_part, 2))
            principal_parts.append(round(principal_part, 2))
            end_balances.append(round(end_balance, 2))

            # Переход к следующему периоду
            current_balance = end_balance
            current_date += relativedelta(months=1)

    # Вывод результатов
    st.success("🎉 Расчет успешно завершен!")

    # Считаем общие метрики для наглядности
    total_paid = sum(payments)
    total_interest = sum(interest_parts)

    # Виджеты-метрики
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Общая сумма выплат", value=f"{total_paid:,.2f} руб.")
    with col2:
        st.metric(label="Переплата по процентам", value=f"{total_interest:,.2f} руб.")
    with col3:
        if payment_type == "Аннуитетный":
            st.metric(label="Ежемесячный платеж", value=f"{payments[0]:,.2f} руб.")
        else:
            st.metric(label="Платеж (1-й / послед.)", value=f"{payments[0]:,.2f} / {payments[-1]:,.2f} руб.")

    # Формирование DataFrame
    schedule_dict = {
        "Дата платежа": dates,
        "Остаток долга на начало": start_balances,
        "Ежемесячный платеж": payments,
        "Процентная часть": interest_parts,
        "Долговая часть": principal_parts,
        "Остаток долга на конец": end_balances
    }

    df_schedule = pd.DataFrame.from_dict(schedule_dict)
    df_schedule.index = df_schedule.index + 1  # Чтобы нумерация месяцев начиналась с 1

    # Отображение таблицы графика платежей
    st.subheader("📊 Подробный график погашения кредита")

    # Используем st.dataframe с красивым форматированием чисел для идеального отображения
    st.dataframe(
        df_schedule,
        use_container_width=True,
        column_config={
            "Остаток долга на начало": st.column_config.NumberColumn(format="%.2f руб."),
            "Ежемесячный платеж": st.column_config.NumberColumn(format="%.2f руб."),
            "Процентная часть": st.column_config.NumberColumn(format="%.2f руб."),
            "Долговая часть": st.column_config.NumberColumn(format="%.2f руб."),
            "Остаток долга на конец": st.column_config.NumberColumn(format="%.2f руб.")
        }
    )

    # Использование st.expander для доп. информации
    with st.expander("ℹ️ Пояснения к расчетам"):
        st.markdown(f"""
        * **Тип платежа**: `{payment_type}`
        * При **аннуитетном** типе вы платите фиксированную сумму каждый месяц, но внутри платежа доля процентов уменьшается, а доля основного долга растет.
        * При **дифференцированном** типе платеж уменьшается к концу срока за счет того, что тело кредита гасится равными долями, а проценты начисляются на тающий остаток.
        """)

    # Использование st.rerun() для сброса приложения
    st.write("") # Небольшой отступ
    if st.button("🔄 Сбросить и очистить расчёты"):
        st.rerun()

else:
    # Сообщение, пока расчет не запущен
    st.info("👈 Заполните параметры кредита в левой панели и нажмите кнопку **'Рассчитать кредит'**.")

import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go

API = "http://localhost:8000"

st.set_page_config(page_title="Electricity Market", layout="wide")
st.title("Рынок электроэнергии России")


def get_data():
    try:
        r = requests.get(f"{API}/records", timeout=5)
        r.raise_for_status()
        return pd.DataFrame(r.json()["data"])
    except requests.exceptions.ConnectionError:
        st.error("Не удалось подключиться к серверу. Запущен ли FastAPI?")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Ошибка при загрузке данных: {e}")
        return pd.DataFrame()


def post_record(payload):
    try:
        r = requests.post(f"{API}/records", json=payload, timeout=5)
        if r.status_code == 201:
            return True, None
        elif r.status_code == 422:
            errors = r.json().get("detail", [])
            msgs = [f"{e['loc'][-1]}: {e['msg']}" for e in errors]
            return False, "\n".join(msgs)
        else:
            return False, r.json().get("detail", "Неизвестная ошибка")
    except requests.exceptions.ConnectionError:
        return False, "Нет соединения с сервером"
    except Exception as e:
        return False, str(e)


def delete_record(record_id):
    try:
        r = requests.delete(f"{API}/records/{record_id}", timeout=5)
        if r.status_code == 200:
            return True, None
        else:
            return False, r.json().get("detail", "Неизвестная ошибка")
    except requests.exceptions.ConnectionError:
        return False, "Нет соединения с сервером"
    except Exception as e:
        return False, str(e)


df = get_data()

st.subheader("Данные")

if df.empty:
    st.info("Нет данных для отображения")
else:
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.caption(f"Записей: {len(df)}")

st.divider()

if not df.empty:
    st.subheader("Графики")

    try:
        df["timestep"] = pd.to_datetime(df["timestep"])
        df = df.sort_values("timestep")
    except Exception:
        pass

    col1, col2 = st.columns(2)

    with col1:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df["timestep"], y=df["consumption_eur"], name="Европа", mode="lines"))
        fig.add_trace(go.Scatter(x=df["timestep"], y=df["consumption_sib"], name="Сибирь", mode="lines"))
        fig.update_layout(title="Потребление", xaxis_title="Время", yaxis_title="МВт·ч", height=400)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=df["timestep"], y=df["price_eur"], name="Европа", mode="lines"))
        fig2.add_trace(go.Scatter(x=df["timestep"], y=df["price_sib"], name="Сибирь", mode="lines"))
        fig2.update_layout(title="Цены", xaxis_title="Время", yaxis_title="руб/МВт·ч", height=400)
        st.plotly_chart(fig2, use_container_width=True)

    st.divider()

st.subheader("Добавить запись")

with st.form("add_form", clear_on_submit=True):
    timestep = st.text_input("Время", placeholder="2006-09-01 00:00")

    col1, col2 = st.columns(2)
    with col1:
        consumption_eur = st.number_input("Потребление Европа", min_value=0.0, step=100.0)
        price_eur = st.number_input("Цена Европа", min_value=0.0, step=1.0)
    with col2:
        consumption_sib = st.number_input("Потребление Сибирь", min_value=0.0, step=100.0)
        price_sib = st.number_input("Цена Сибирь", min_value=0.0, step=1.0)

    if st.form_submit_button("Добавить"):
        if not timestep.strip():
            st.error("Укажите время")
        else:
            ok, err = post_record({
                "timestep": timestep.strip(),
                "consumption_eur": consumption_eur,
                "consumption_sib": consumption_sib,
                "price_eur": price_eur,
                "price_sib": price_sib
            })
            if ok:
                st.success("Готово")
                st.rerun()
            else:
                st.error(err)

st.divider()

st.subheader("Удалить запись")

if df.empty:
    st.info("Нет записей для удаления")
else:
    record_id = st.selectbox("ID записи", options=df["id"].tolist())

    st.dataframe(df[df["id"] == record_id], use_container_width=True, hide_index=True)

    if st.button("Удалить"):
        ok, err = delete_record(record_id)
        if ok:
            st.success("Удалено")
            st.rerun()
        else:
            st.error(err)

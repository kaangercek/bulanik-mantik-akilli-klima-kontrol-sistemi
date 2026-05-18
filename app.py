from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pyarrow as pa
import streamlit as st

from src.fuzzy_climate_controller import FuzzyClimateController, FuzzyResult


st.set_page_config(
    page_title="Bulanık Mantık Klima Kontrol Sistemi",
    page_icon="🌡️",
    layout="wide",
)


def apply_theme() -> None:
    st.markdown(
        """
        <style>
            .stApp {
                background:
                    radial-gradient(circle at top left, rgba(255, 183, 77, 0.20), transparent 22%),
                    radial-gradient(circle at top right, rgba(0, 150, 136, 0.14), transparent 20%),
                    linear-gradient(180deg, #f6f1e8 0%, #edf6f5 100%);
                color: #173042;
                font-family: "Trebuchet MS", "Segoe UI", sans-serif;
            }
            [data-testid="stSidebar"] {
                background: linear-gradient(180deg, #0b3c49 0%, #176b73 100%);
            }
            [data-testid="stSidebar"] * {
                color: #f5fbfb;
            }
            .hero-card {
                background: rgba(255, 255, 255, 0.90);
                border: 1px solid rgba(23, 48, 66, 0.08);
                border-radius: 18px;
                padding: 1.1rem 1.2rem;
                box-shadow: 0 12px 30px rgba(23, 48, 66, 0.08);
                min-height: 132px;
            }
            .hero-label {
                font-size: 0.92rem;
                letter-spacing: 0.02em;
                text-transform: uppercase;
                color: #51707d;
                margin-bottom: 0.35rem;
            }
            .hero-value {
                font-size: 2rem;
                font-weight: 700;
                color: #173042;
                margin-bottom: 0.25rem;
            }
            .hero-note {
                font-size: 0.95rem;
                color: #51707d;
            }
            .section-note {
                background: rgba(255, 255, 255, 0.72);
                border-left: 4px solid #ef8354;
                border-radius: 12px;
                padding: 0.9rem 1rem;
                margin: 0.8rem 0 1rem 0;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_resource
def get_controller() -> FuzzyClimateController:
    return FuzzyClimateController()


def initialize_inputs() -> None:
    defaults = {
        "temperature": 26.0,
        "humidity": 58.0,
        "room_size": 32.0,
    }
    for key, value in defaults.items():
        slider_key = f"{key}_slider"
        number_key = f"{key}_number"
        if slider_key not in st.session_state:
            st.session_state[slider_key] = value
        if number_key not in st.session_state:
            st.session_state[number_key] = value


def sync_from_slider(prefix: str) -> None:
    st.session_state[f"{prefix}_number"] = st.session_state[f"{prefix}_slider"]


def sync_from_number(prefix: str) -> None:
    st.session_state[f"{prefix}_slider"] = st.session_state[f"{prefix}_number"]


def summary_card(title: str, value: str, note: str) -> str:
    return f"""
    <div class="hero-card">
        <div class="hero-label">{title}</div>
        <div class="hero-value">{value}</div>
        <div class="hero-note">{note}</div>
    </div>
    """


def plot_membership_functions(controller: FuzzyClimateController, result: FuzzyResult):
    figure, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.flatten()
    palette = ["#ef8354", "#2a9d8f", "#3d5a80", "#8d5fd3", "#d1495b"]

    for axis, variable_key in zip(axes[:3], controller.input_order):
        variable = controller.variables[variable_key]
        current_value = result.inputs[variable_key]
        for color, (term, function) in zip(palette, variable.terms.items()):
            curve = function(variable.universe)
            axis.plot(variable.universe, curve, color=color, linewidth=2.2, label=term)
            current_degree = result.fuzzified[variable_key][term]
            if current_degree > 0:
                axis.scatter(
                    [current_value],
                    [current_degree],
                    color=color,
                    s=65,
                    zorder=4,
                )
        axis.axvline(current_value, color="#173042", linestyle="--", linewidth=1.4)
        axis.set_title(f"{variable.label} Üyelik Fonksiyonları", fontsize=12)
        axis.set_xlabel(f"{variable.label} ({variable.unit})")
        axis.set_ylabel("Üyelik Derecesi")
        axis.set_ylim(-0.02, 1.05)
        axis.grid(alpha=0.24)
        axis.legend(frameon=False)

    output_variable = controller.variables[controller.output_key]
    output_axis = axes[3]
    for color, (term, function) in zip(palette, output_variable.terms.items()):
        clipped_curve = np.minimum(
            result.consequent_strengths[term],
            function(output_variable.universe),
        )
        output_axis.plot(
            output_variable.universe,
            function(output_variable.universe),
            color=color,
            linestyle=":",
            linewidth=1.4,
        )
        output_axis.fill_between(
            output_variable.universe,
            0,
            clipped_curve,
            color=color,
            alpha=0.28,
            label=f"{term} ({result.consequent_strengths[term]:.2f})",
        )
    output_axis.set_title("Çıktı Terimlerinin Aktivasyonu", fontsize=12)
    output_axis.set_xlabel(f"{output_variable.label} ({output_variable.unit})")
    output_axis.set_ylabel("Üyelik Derecesi")
    output_axis.set_ylim(-0.02, 1.05)
    output_axis.grid(alpha=0.24)
    output_axis.legend(frameon=False)

    figure.tight_layout()
    return figure


def plot_output_aggregation(controller: FuzzyClimateController, result: FuzzyResult):
    output_variable = controller.variables[controller.output_key]
    figure, axis = plt.subplots(figsize=(9.5, 4.6))
    palette = ["#ef8354", "#2a9d8f", "#3d5a80", "#8d5fd3", "#d1495b"]

    for color, (term, function) in zip(palette, output_variable.terms.items()):
        axis.plot(
            output_variable.universe,
            function(output_variable.universe),
            linewidth=1.4,
            color=color,
            alpha=0.8,
            label=term,
        )

    axis.fill_between(
        output_variable.universe,
        0,
        result.aggregated_output,
        color="#d62839",
        alpha=0.32,
        label="Birikik çıktı",
    )
    axis.axvline(
        result.crisp_output,
        color="#173042",
        linestyle="--",
        linewidth=2,
        label=f"Centroid = {result.crisp_output:.2f}%",
    )
    axis.set_title("Durulaştırma Sonucu (Ağırlık Merkezi / Centroid)", fontsize=12)
    axis.set_xlabel(f"{output_variable.label} ({output_variable.unit})")
    axis.set_ylabel("Üyelik Derecesi")
    axis.set_ylim(-0.02, 1.05)
    axis.grid(alpha=0.24)
    axis.legend(frameon=False, ncol=3)
    figure.tight_layout()
    return figure


def to_arrow_table(rows: list[dict[str, object]]) -> pa.Table:
    if not rows:
        return pa.table({"Bilgi": ["Gösterilecek veri bulunamadı."]})
    return pa.Table.from_pylist(rows)


def plot_rule_activations(active_rules: list[dict[str, object]]):
    figure, axis = plt.subplots(figsize=(8.8, 4.6))
    ordered = sorted(active_rules, key=lambda row: float(row["Aktivasyon"]))
    axis.barh(
        [row["Kural"] for row in ordered],
        [float(row["Aktivasyon"]) for row in ordered],
        color="#2a9d8f",
        alpha=0.88,
    )
    axis.set_xlim(0, 1.0)
    axis.set_xlabel("Aktivasyon Derecesi")
    axis.set_title("Aktif Kuralların Aktivasyon Grafiği", fontsize=12)
    axis.grid(axis="x", alpha=0.24)
    figure.tight_layout()
    return figure


def build_active_rule_rows(result: FuzzyResult) -> list[dict[str, object]]:
    rows = []
    for activation in result.rule_activations:
        if activation.activation > 0:
            rows.append(
                {
                    "Kural": f"Kural {activation.index}",
                    "Aktivasyon": round(activation.activation, 4),
                    "Sonuç": activation.consequent,
                    "Açıklama": activation.description,
                }
            )
    return sorted(rows, key=lambda row: float(row["Aktivasyon"]), reverse=True)


def build_fuzzification_rows(
    result: FuzzyResult,
    controller: FuzzyClimateController,
) -> list[dict[str, object]]:
    rows = []
    for variable_key in controller.input_order:
        variable = controller.variables[variable_key]
        for term, degree in result.fuzzified[variable_key].items():
            rows.append(
                {
                    "Değişken": variable.label,
                    "Terim": term,
                    "Derece": round(degree, 4),
                }
            )
    return rows


def build_scenario_rows(controller: FuzzyClimateController) -> list[dict[str, object]]:
    rows = []
    for scenario in controller.default_scenarios():
        inputs = {
            "temperature": float(scenario["temperature"]),
            "humidity": float(scenario["humidity"]),
            "room_size": float(scenario["room_size"]),
        }
        result = controller.evaluate(inputs)
        rows.append(
            {
                "Senaryo": scenario["Senaryo"],
                "Sıcaklık (°C)": inputs["temperature"],
                "Nem (%)": inputs["humidity"],
                "Oda Büyüklüğü (m²)": inputs["room_size"],
                "Fan Hızı (%)": round(result.crisp_output, 2),
                "Baskın Çıkış": result.dominant_output,
                "Yorum": controller.interpret_fan_speed(result.crisp_output),
            }
        )
    return rows


def plot_scenario_results(scenario_rows: list[dict[str, object]]):
    figure, axis = plt.subplots(figsize=(10.0, 4.6))
    axis.bar(
        [row["Senaryo"] for row in scenario_rows],
        [float(row["Fan Hızı (%)"]) for row in scenario_rows],
        color=["#ef8354", "#2a9d8f", "#3d5a80", "#8d5fd3", "#d1495b", "#457b9d"],
    )
    axis.set_title("Farklı Senaryolarda Fan Hızı Sonuçları", fontsize=12)
    axis.set_ylabel("Fan Hızı (%)")
    axis.set_ylim(0, 100)
    axis.grid(axis="y", alpha=0.24)
    axis.tick_params(axis="x", rotation=20)
    figure.tight_layout()
    return figure


def main() -> None:
    apply_theme()
    controller = get_controller()
    initialize_inputs()

    st.title("Bulanık Mantık Tabanlı Akıllı Klima Kontrol Sistemi")
    st.caption(
        "Mamdani tipi bulanık çıkarım, min-max birleştirme ve centroid durulaştırma "
        "kullanılarak geliştirilen etkileşimli proje arayüzü."
    )

    with st.sidebar:
        st.header("Kontrol Paneli")
        st.write("Giriş değerlerini slider veya sayısal kutu ile değiştir.")

        temp_col, temp_number_col = st.columns([3, 1.1])
        with temp_col:
            st.slider(
                "Sıcaklık (°C)",
                min_value=16.0,
                max_value=36.0,
                step=0.5,
                key="temperature_slider",
                on_change=sync_from_slider,
                args=("temperature",),
            )
        with temp_number_col:
            st.number_input(
                "°C",
                min_value=16.0,
                max_value=36.0,
                step=0.5,
                key="temperature_number",
                on_change=sync_from_number,
                args=("temperature",),
            )

        humidity_col, humidity_number_col = st.columns([3, 1.1])
        with humidity_col:
            st.slider(
                "Nem (%)",
                min_value=20.0,
                max_value=90.0,
                step=1.0,
                key="humidity_slider",
                on_change=sync_from_slider,
                args=("humidity",),
            )
        with humidity_number_col:
            st.number_input(
                "%",
                min_value=20.0,
                max_value=90.0,
                step=1.0,
                key="humidity_number",
                on_change=sync_from_number,
                args=("humidity",),
            )

        room_col, room_number_col = st.columns([3, 1.1])
        with room_col:
            st.slider(
                "Oda Büyüklüğü (m²)",
                min_value=10.0,
                max_value=60.0,
                step=1.0,
                key="room_size_slider",
                on_change=sync_from_slider,
                args=("room_size",),
            )
        with room_number_col:
            st.number_input(
                "m²",
                min_value=10.0,
                max_value=60.0,
                step=1.0,
                key="room_size_number",
                on_change=sync_from_number,
                args=("room_size",),
            )

        calculate_clicked = st.button("Hesapla", use_container_width=True, type="primary")
        st.info("Grafikler değerler değiştikçe otomatik güncellenir; buton mevcut durumu öne çıkarır.")

    inputs = {
        "temperature": float(st.session_state["temperature_slider"]),
        "humidity": float(st.session_state["humidity_slider"]),
        "room_size": float(st.session_state["room_size_slider"]),
    }
    result = controller.evaluate(inputs)
    active_rule_rows = build_active_rule_rows(result)
    fuzzification_rows = build_fuzzification_rows(result, controller)
    scenario_rows = build_scenario_rows(controller)

    if calculate_clicked:
        st.success(
            f"Fan hızı %{result.crisp_output:.2f} olarak hesaplandı. "
            f"Baskın dilsel çıktı: {result.dominant_output}."
        )

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            summary_card(
                "Durulaştırılmış Çıktı",
                f"%{result.crisp_output:.2f}",
                controller.interpret_fan_speed(result.crisp_output),
            ),
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            summary_card(
                "Baskın Çıkış Terimi",
                result.dominant_output,
                "En yüksek üyelik derecesine sahip fan hızı seviyesi.",
            ),
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            summary_card(
                "Aktif Kural Sayısı",
                str(len(active_rule_rows)),
                "Sıfırdan büyük aktivasyona sahip kurallar listelenir.",
            ),
            unsafe_allow_html=True,
        )

    tabs = st.tabs(
        [
            "Canlı Kontrol",
            "Üyelik Fonksiyonları",
            "Senaryo Testleri",
            "Kural Tabanı",
        ]
    )

    with tabs[0]:
        st.markdown(
            """
            <div class="section-note">
                Giriş değişkenleri değiştikçe sistem yeni bulanıklaştırma, çıkarım ve
                durulaştırma adımlarını otomatik olarak hesaplar.
            </div>
            """,
            unsafe_allow_html=True,
        )
        chart_col, rules_col = st.columns([1.2, 1.0])
        with chart_col:
            st.pyplot(plot_output_aggregation(controller, result), use_container_width=True)
        with rules_col:
            if not active_rule_rows:
                st.warning("Bu giriş kombinasyonunda aktif kural bulunamadı.")
            else:
                st.pyplot(plot_rule_activations(active_rule_rows), use_container_width=True)
                st.dataframe(to_arrow_table(active_rule_rows), use_container_width=True, hide_index=True)

        st.subheader("Bulanıklaştırma Tablosu")
        st.dataframe(to_arrow_table(fuzzification_rows), use_container_width=True, hide_index=True)

    with tabs[1]:
        st.pyplot(plot_membership_functions(controller, result), use_container_width=True)

    with tabs[2]:
        st.markdown(
            """
            <div class="section-note">
                Aşağıdaki senaryolar, projede kullanılabilecek test örnekleridir.
                Böylece sistemin farklı ortam koşullarına verdiği tepkiler karşılaştırılabilir.
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.dataframe(to_arrow_table(scenario_rows), use_container_width=True, hide_index=True)
        st.pyplot(plot_scenario_results(scenario_rows), use_container_width=True)

    with tabs[3]:
        st.subheader("27 Kurallı Mamdani Kural Tabanı")
        st.dataframe(to_arrow_table(controller.get_rule_table()), use_container_width=True, hide_index=True)
        st.markdown(
            """
            `AND` işlemi için `min`, kural birleştirme için `max`, durulaştırma için
            `centroid` yöntemi kullanılmaktadır.
            """
        )


if __name__ == "__main__":
    main()

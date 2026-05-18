from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np


def triangular_mf(x: np.ndarray | float, a: float, b: float, c: float) -> np.ndarray | float:
    values = np.asarray(x, dtype=float)
    membership = np.zeros_like(values)

    rising = (a < values) & (values < b)
    falling = (b < values) & (values < c)

    if b != a:
        membership[rising] = (values[rising] - a) / (b - a)
    if c != b:
        membership[falling] = (c - values[falling]) / (c - b)

    membership[values == b] = 1.0
    return float(membership) if membership.ndim == 0 else membership


def trapezoidal_mf(
    x: np.ndarray | float,
    a: float,
    b: float,
    c: float,
    d: float,
) -> np.ndarray | float:
    values = np.asarray(x, dtype=float)
    membership = np.zeros_like(values)

    rising = (a < values) & (values < b)
    top = (b <= values) & (values <= c)
    falling = (c < values) & (values < d)

    if b != a:
        membership[rising] = (values[rising] - a) / (b - a)
    if d != c:
        membership[falling] = (d - values[falling]) / (d - c)

    membership[top] = 1.0
    return float(membership) if membership.ndim == 0 else membership


@dataclass(frozen=True)
class FuzzyVariable:
    key: str
    label: str
    unit: str
    universe: np.ndarray
    terms: dict[str, Callable[[np.ndarray | float], np.ndarray | float]]


@dataclass(frozen=True)
class FuzzyRule:
    index: int
    antecedents: dict[str, str]
    consequent: str
    description: str


@dataclass(frozen=True)
class RuleActivation:
    index: int
    description: str
    consequent: str
    activation: float


@dataclass(frozen=True)
class FuzzyResult:
    inputs: dict[str, float]
    fuzzified: dict[str, dict[str, float]]
    rule_activations: list[RuleActivation]
    consequent_strengths: dict[str, float]
    aggregated_output: np.ndarray
    crisp_output: float
    output_memberships: dict[str, float]
    dominant_output: str


class FuzzyClimateController:
    def __init__(self) -> None:
        self.variables = self._build_variables()
        self.rules = self._build_rules()
        self.input_order = ["temperature", "humidity", "room_size"]
        self.output_key = "fan_speed"

    def _build_variables(self) -> dict[str, FuzzyVariable]:
        return {
            "temperature": FuzzyVariable(
                key="temperature",
                label="Sıcaklık",
                unit="°C",
                universe=np.linspace(16.0, 36.0, 800),
                terms={
                    "Düşük": lambda x: trapezoidal_mf(x, 16.0, 16.0, 18.0, 22.0),
                    "Konforlu": lambda x: triangular_mf(x, 20.0, 24.0, 28.0),
                    "Yüksek": lambda x: trapezoidal_mf(x, 26.0, 30.0, 36.0, 36.0),
                },
            ),
            "humidity": FuzzyVariable(
                key="humidity",
                label="Nem",
                unit="%",
                universe=np.linspace(20.0, 90.0, 800),
                terms={
                    "Kuru": lambda x: trapezoidal_mf(x, 20.0, 20.0, 30.0, 45.0),
                    "Normal": lambda x: triangular_mf(x, 40.0, 55.0, 70.0),
                    "Nemli": lambda x: trapezoidal_mf(x, 65.0, 75.0, 90.0, 90.0),
                },
            ),
            "room_size": FuzzyVariable(
                key="room_size",
                label="Oda Büyüklüğü",
                unit="m²",
                universe=np.linspace(10.0, 60.0, 800),
                terms={
                    "Küçük": lambda x: trapezoidal_mf(x, 10.0, 10.0, 18.0, 28.0),
                    "Orta": lambda x: triangular_mf(x, 22.0, 35.0, 48.0),
                    "Büyük": lambda x: trapezoidal_mf(x, 42.0, 50.0, 60.0, 60.0),
                },
            ),
            "fan_speed": FuzzyVariable(
                key="fan_speed",
                label="Fan Hızı",
                unit="%",
                universe=np.linspace(0.0, 100.0, 1200),
                terms={
                    "Çok Düşük": lambda x: trapezoidal_mf(x, 0.0, 0.0, 10.0, 25.0),
                    "Düşük": lambda x: triangular_mf(x, 15.0, 30.0, 45.0),
                    "Orta": lambda x: triangular_mf(x, 35.0, 50.0, 65.0),
                    "Yüksek": lambda x: triangular_mf(x, 55.0, 70.0, 85.0),
                    "Çok Yüksek": lambda x: trapezoidal_mf(x, 75.0, 90.0, 100.0, 100.0),
                },
            ),
        }

    def _build_rules(self) -> list[FuzzyRule]:
        rule_rows = [
            ("Düşük", "Kuru", "Küçük", "Çok Düşük"),
            ("Düşük", "Kuru", "Orta", "Düşük"),
            ("Düşük", "Kuru", "Büyük", "Düşük"),
            ("Düşük", "Normal", "Küçük", "Düşük"),
            ("Düşük", "Normal", "Orta", "Düşük"),
            ("Düşük", "Normal", "Büyük", "Orta"),
            ("Düşük", "Nemli", "Küçük", "Düşük"),
            ("Düşük", "Nemli", "Orta", "Orta"),
            ("Düşük", "Nemli", "Büyük", "Orta"),
            ("Konforlu", "Kuru", "Küçük", "Düşük"),
            ("Konforlu", "Kuru", "Orta", "Orta"),
            ("Konforlu", "Kuru", "Büyük", "Orta"),
            ("Konforlu", "Normal", "Küçük", "Orta"),
            ("Konforlu", "Normal", "Orta", "Orta"),
            ("Konforlu", "Normal", "Büyük", "Yüksek"),
            ("Konforlu", "Nemli", "Küçük", "Orta"),
            ("Konforlu", "Nemli", "Orta", "Yüksek"),
            ("Konforlu", "Nemli", "Büyük", "Yüksek"),
            ("Yüksek", "Kuru", "Küçük", "Orta"),
            ("Yüksek", "Kuru", "Orta", "Yüksek"),
            ("Yüksek", "Kuru", "Büyük", "Yüksek"),
            ("Yüksek", "Normal", "Küçük", "Yüksek"),
            ("Yüksek", "Normal", "Orta", "Yüksek"),
            ("Yüksek", "Normal", "Büyük", "Çok Yüksek"),
            ("Yüksek", "Nemli", "Küçük", "Yüksek"),
            ("Yüksek", "Nemli", "Orta", "Çok Yüksek"),
            ("Yüksek", "Nemli", "Büyük", "Çok Yüksek"),
        ]

        rules: list[FuzzyRule] = []
        for index, (temperature, humidity, room_size, fan_speed) in enumerate(rule_rows, start=1):
            description = (
                f"EĞER sıcaklık {temperature} VE nem {humidity} VE oda büyüklüğü {room_size} "
                f"İSE fan hızı {fan_speed}"
            )
            rules.append(
                FuzzyRule(
                    index=index,
                    antecedents={
                        "temperature": temperature,
                        "humidity": humidity,
                        "room_size": room_size,
                    },
                    consequent=fan_speed,
                    description=description,
                )
            )
        return rules

    def fuzzify(self, inputs: dict[str, float]) -> dict[str, dict[str, float]]:
        fuzzified: dict[str, dict[str, float]] = {}
        for variable_key in self.input_order:
            variable = self.variables[variable_key]
            fuzzified[variable_key] = {
                term: float(function(inputs[variable_key]))
                for term, function in variable.terms.items()
            }
        return fuzzified

    def evaluate(self, inputs: dict[str, float]) -> FuzzyResult:
        fuzzified = self.fuzzify(inputs)
        output_variable = self.variables[self.output_key]
        aggregated_output = np.zeros_like(output_variable.universe)
        consequent_strengths = {term: 0.0 for term in output_variable.terms}
        rule_activations: list[RuleActivation] = []

        for rule in self.rules:
            activation = min(
                fuzzified[variable_key][term]
                for variable_key, term in rule.antecedents.items()
            )
            consequent_strengths[rule.consequent] = max(
                consequent_strengths[rule.consequent],
                activation,
            )

            clipped_output = np.minimum(
                activation,
                output_variable.terms[rule.consequent](output_variable.universe),
            )
            aggregated_output = np.maximum(aggregated_output, clipped_output)
            rule_activations.append(
                RuleActivation(
                    index=rule.index,
                    description=rule.description,
                    consequent=rule.consequent,
                    activation=float(activation),
                )
            )

        denominator = np.trapz(aggregated_output, output_variable.universe)
        if denominator == 0:
            crisp_output = 0.0
        else:
            numerator = np.trapz(output_variable.universe * aggregated_output, output_variable.universe)
            crisp_output = float(numerator / denominator)

        output_memberships = {
            term: float(function(crisp_output))
            for term, function in output_variable.terms.items()
        }
        dominant_output = max(output_memberships, key=output_memberships.get)

        return FuzzyResult(
            inputs=inputs,
            fuzzified=fuzzified,
            rule_activations=rule_activations,
            consequent_strengths=consequent_strengths,
            aggregated_output=aggregated_output,
            crisp_output=crisp_output,
            output_memberships=output_memberships,
            dominant_output=dominant_output,
        )

    def get_rule_table(self) -> list[dict[str, str]]:
        table: list[dict[str, str]] = []
        for rule in self.rules:
            table.append(
                {
                    "Kural": f"Kural {rule.index}",
                    "Sıcaklık": rule.antecedents["temperature"],
                    "Nem": rule.antecedents["humidity"],
                    "Oda Büyüklüğü": rule.antecedents["room_size"],
                    "Fan Hızı": rule.consequent,
                }
            )
        return table

    def default_scenarios(self) -> list[dict[str, float | str]]:
        return [
            {
                "Senaryo": "Serin ve kuru küçük oda",
                "temperature": 18.0,
                "humidity": 32.0,
                "room_size": 16.0,
            },
            {
                "Senaryo": "Konforlu orta oda",
                "temperature": 24.0,
                "humidity": 52.0,
                "room_size": 32.0,
            },
            {
                "Senaryo": "Konforlu ama nemli büyük oda",
                "temperature": 25.0,
                "humidity": 74.0,
                "room_size": 52.0,
            },
            {
                "Senaryo": "Sıcak ve kuru orta oda",
                "temperature": 31.0,
                "humidity": 38.0,
                "room_size": 34.0,
            },
            {
                "Senaryo": "Sıcak ve nemli büyük oda",
                "temperature": 34.0,
                "humidity": 84.0,
                "room_size": 58.0,
            },
            {
                "Senaryo": "Serin ama nemli büyük oda",
                "temperature": 20.0,
                "humidity": 78.0,
                "room_size": 55.0,
            },
        ]

    def interpret_fan_speed(self, value: float) -> str:
        if value < 20:
            return "Klima çok düşük güçte çalışmalı."
        if value < 40:
            return "Klima düşük seviyede çalışmalı."
        if value < 60:
            return "Klima orta seviyede çalışmalı."
        if value < 80:
            return "Klima yüksek seviyede çalışmalı."
        return "Klima çok yüksek seviyede çalışmalı."

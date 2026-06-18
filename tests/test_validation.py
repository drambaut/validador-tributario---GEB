from case_registry import CASES
from text_utils import money, names_equivalent
from validation_engine import validate_case


def test_normalization():
    assert money("5.491.000") == 5_491_000
    assert names_equivalent("GRUPO ENERGIA BOGOTA S A ESP - SIGLA GEB", "GRUPO ENERGIA BOGOTÄ SA ESP")


def test_ica_real_case():
    report = validate_case(CASES[("Ciénaga", "ICA anual")])
    assert report["summary"]["total"] == 27
    assert report["summary"]["cumple"] >= 15
    result = next(x for x in report["results"] if "base gravable" in x["validation"].lower())
    assert result["status"] == "cumple"

from aiok.config import cors_origin_list


def test_cors_origin_list_star():
    assert cors_origin_list("*") == ["*"]


def test_cors_origin_list_multiple():
    assert cors_origin_list("https://a.example, https://b.example") == [
        "https://a.example",
        "https://b.example",
    ]

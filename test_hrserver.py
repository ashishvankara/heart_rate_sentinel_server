import pytest

@pytest.mark.parametrize("user_age, hr, expected",[
    (10/365, 200, True),
    (10/365, 170, False),
    (1.5, 170, True),
    (1.5, 80, False),
    (20, 900, True),
    (20, 90, False)
])
def test_istachycardic(user_age, hr, expected):
    """" Tests tachycardic
    """
    from hrserver import istachycardic
    a = istachycardic(user_age, hr)
    assert a == expected


import pytest


@pytest.mark.parametrize("user_age, hr, expected", [
    (10/365, 200, True),
    (10/365, 170, False),
    (1.5, 170, True),
    (1.5, 80, False),
    (20, 900, True),
    (20, 90, False)
])
def test_istachycardic(user_age, hr, expected):
    """ Tests istachycardic()

    """
    from hrserver import istachycardic
    a = istachycardic(user_age, hr)
    assert a == expected


def test_averageHR():
    """ Tests averageHR() calculations

    """
    from hrserver import averageHR
    import numpy as np
    a = np.arange(1, 15)
    calculated_avg = averageHR(a)
    assert pytest.approx(calculated_avg) == a.mean()


def test_recondition():
    """ Tests recondition()

    """
    import numpy as np
    from datetime import datetime, timedelta
    from hrserver import recondition
    t = np.arange(datetime(2018, 11, 11, 12, 1),
                  datetime(2018, 11, 11, 12, 6),
                  timedelta(minutes=1)).astype(datetime)
    hr_since = datetime(2018, 11, 11, 12, 3)
    mockhr = np.arange(0, 5)
    reconditioned_hr = recondition(hr_since, t, mockhr)
    assert reconditioned_hr == [2, 3, 4]

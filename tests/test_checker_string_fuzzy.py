import pytest

from vakt.checker import StringFuzzyChecker
from vakt.policy import Policy


@pytest.mark.parametrize('policy, field, what, result', [
    (Policy('1', actions=['get']), 'actions', 'get', True),
    (Policy('1', actions=['get']), 'actions', 'g', True),
    (Policy('1', actions=['get']), 'actions', 'et', True),
    (Policy('1', actions=['get']), 'actions', 't', True),
    (Policy('1', actions=['get', 'list']), 'actions', 'list', True),
    (Policy('1', actions=['get', 'list']), 'non_existing_field', 'get', False),
    (Policy('1', actions=['<get>']), 'actions', 'get', True),
    (Policy('1', actions=['<get>']), 'actions', 'e', True),
    (Policy('1', actions=['<get>']), 'actions', '<get>', False),
    (Policy('1', actions=['<get>']), 'actions', '<t>', False),
    (Policy('1', actions=['<get']), 'actions', 'get', True),
    (Policy('1', actions=['<get']), 'actions', 'ge', True),
    (Policy('1', resources=['books:1', 'books:2']), 'resources', 'books', True),
    (Policy('1', resources=['books:1', 'books:2']), 'resources', ':', True),
    (Policy('1', resources=['books:1', 'books:2']), 'resources', '3', False),
])
def test_matches(policy, field, what, result):
    c = StringFuzzyChecker()
    assert result == c.fits(policy, field, what)

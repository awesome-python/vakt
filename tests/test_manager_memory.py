import pytest

from vakt.managers.memory import MemoryManager
from vakt.policy import DefaultPolicy
from vakt.exceptions import PolicyExists


@pytest.fixture
def pm():
    return MemoryManager()


def test_create(pm):
    pm.create(DefaultPolicy('1', description='foo'))
    assert '1' == pm.get('1').id
    assert 'foo' == pm.get('1').description


def test_policy_create_existing(pm):
    pm.create(DefaultPolicy('1', description='foo'))
    with pytest.raises(PolicyExists):
        pm.create(DefaultPolicy('1', description='bar'))


def test_get(pm):
    pm.create(DefaultPolicy('1'))
    pm.create(DefaultPolicy(2, description='some text'))
    assert isinstance(pm.get('1'), DefaultPolicy)
    assert '1' == pm.get('1').id
    assert 2 == pm.get(2).id
    assert 'some text' == pm.get(2).description


def test_get_all(pm):
    assert 0 == 1

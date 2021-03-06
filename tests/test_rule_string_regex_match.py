import pytest

from vakt.rules.string import RegexMatchRule


def test_regex_match_construct_fails():
    with pytest.raises(TypeError) as excinfo:
        RegexMatchRule('[lll')
    assert 'pattern should be a valid regexp string' in str(excinfo.value)
    assert 'unterminated character set at position 0' in str(excinfo.value) \
           or 'unexpected end of regular expression' in str(excinfo.value)


@pytest.mark.parametrize('arg, against, result', [
    ('.*', 'foo', True),
    ('aaa', 'aaa', True),
    ('aaa', 'aab', False),
    ('[\d\w]+', '567asd', True),
    ('', '', True),
    ('^python\?exe$', 'python?exe', True),
    ('^python?exe$', 'python?exe', False),
])
def test_regex_match_rule_satisfied(arg, against, result):
    c = RegexMatchRule(arg)
    assert result == c.satisfied(against)

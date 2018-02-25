import re
import logging
from abc import ABCMeta, abstractmethod

from .compiler import compile_regex
from .exceptions import InvalidPattern


log = logging.getLogger(__name__)


class RegexMatcher:
    """Matcher that uses regular expressions."""

    def matches(self, policy, field, what):
        where = getattr(policy, field, [])
        for i in where:
            if policy.start_delimiter not in i:  # check if 'where' item is written in a policy-defined-regex syntax.
                if i == what:  # it's a single string match
                    return True
                continue
            try:
                pattern = compile_regex(i, policy.start_delimiter, policy.end_delimiter)
            except InvalidPattern:
                log.exception('Error matching policy, because of failed regex %s compilation', i)
                return False
            if re.match(pattern, what):
                return True
        return False


class StringMatcher(metaclass=ABCMeta):
    """Matcher that uses string equality."""

    def matches(self, policy, field, what):
        where = getattr(policy, field, [])
        for item in where:
            if policy.start_delimiter == item[0] and policy.end_delimiter == item[-1]:
                item = item[1:-1]
            if self.compare(what, item):
                    return True
            continue
        return False

    @abstractmethod
    def compare(self, needle, haystack):
        pass


class StringExactMatcher(StringMatcher):
    """
    Matcher that uses exact string equality. Case-sensitive.
    E.g. 'sun' in 'sunny' - False
         'sun' in 'sun' - True
    """

    def compare(self, needle, haystack):
        return needle == haystack


class StringFuzzyMatcher(StringMatcher):
    """
    Matcher that uses fuzzy substring string equality. Case-sensitive.
    E.g. 'sun' in 'sunny' - True
         'sun' in 'sun' - True
    """

    def compare(self, needle, haystack):
        return needle in haystack

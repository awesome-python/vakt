""""
Main module that serves as an entry point for Vakt decisions.
Also contains Inquiry class.
"""

import logging

from .util import JsonSerializer, PrettyPrint
from .audit import get_logger as audit_logger


log = logging.getLogger(__name__)
audit_log = audit_logger()


class Inquiry(JsonSerializer, PrettyPrint):
    """Holds all the information about the inquired intent.
    Is responsible to decisions is the inquired intent allowed or not."""

    def __init__(self, resource=None, action=None, subject=None, context=None):
        # explicitly assign empty strings instead of occasional None, (), etc.
        self.resource = resource or ''
        self.action = action or ''
        self.subject = subject or ''
        self.context = context or {}

    @classmethod
    def from_json(cls, data):
        props = cls._parse(data)
        return cls(**props)


class Guard:
    """Executor of policy checks.
       Given a storage and a checker it can decide via `is_allowed` method if a given inquiry allowed or not."""

    def __init__(self, storage, checker):
        self.storage = storage
        self.checker = checker

    def is_allowed(self, inquiry):
        """Is given inquiry intent allowed or not?"""
        try:
            policies = self.storage.find_for_inquiry(inquiry, self.checker)
            # Storage is not obliged to do the exact policies match. It's up to the storage
            # to decide what policies to return. So we need a more correct programmatically done check.
            answer = self.check_policies_allow(inquiry, policies)
        except Exception:
            log.exception('Unexpected exception occurred while checking Inquiry %s', inquiry)
            answer = False

        if answer:
            audit_log.info('Incoming Inquiry was allowed. Inquiry: %s', inquiry)
        else:
            audit_log.info('Incoming Inquiry was rejected. Inquiry: %s', inquiry)

        return answer

    def check_policies_allow(self, inquiry, policies):
        """
        Check if any of a given policy allows a specified inquiry
        """
        audit_log.info("Potential Policies for Inquiry '%s' are: %s", inquiry, policies)

        # If no policies found or None is given -> deny access!
        if not policies:
            return False

        # Filter policies that fit Inquiry by its attributes.
        filtered = [p for p in policies if
                    self.checker.fits(p, 'actions', inquiry.action) and
                    self.checker.fits(p, 'subjects', inquiry.subject) and
                    self.checker.fits(p, 'resources', inquiry.resource) and
                    self.are_rules_satisfied(p, inquiry)]

        audit_log.info("Policies filtered by checker '%s' for Inquiry '%s' are: %s", self.checker, inquiry, policies)

        # no policies -> deny access!
        # if we have 2 or more similar policies - all of them should have allow effect, otherwise -> deny access!
        return len(filtered) > 0 and all(p.allow_access() for p in filtered)

    @staticmethod
    def are_rules_satisfied(policy, inquiry):
        """
        Check if rules in the policy are satisfied for a given inquiry's context.
        If at least one rule is not present in Inquiry's context -> deny access.
        If at least one rule provided in Inquiry's context is not satisfied -> deny access.
        """
        for key, rule in policy.rules.items():
            try:
                ctx_value = inquiry.context[key]
            except KeyError:
                log.debug("No key '%s' found in Inquiry context", key)
                return False
            if not rule.satisfied(ctx_value, inquiry):
                return False
        return True

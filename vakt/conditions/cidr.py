import ipaddress
from vakt.conditions.base import Condition


class CIDRCondition(Condition):
    """Condition that is fulfilled when request's IP address is in the provided CIDR"""

    def __init__(self, cidr):
        self.cidr = cidr

    def ok(self, what, request):
        if not isinstance(what, str):
            return False
        try:
            ip = ipaddress.ip_address(what)
            net = ipaddress.ip_network(self.cidr)
        except ValueError as e:
            # todo - add logging
            return False
        return ip in net

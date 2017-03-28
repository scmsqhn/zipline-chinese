#
# Copyright 2014 Quantopian, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from six import iteritems

from zipline.utils.serialization_utils import (
    VERSION_LABEL
)


class PerShare(object):
    """
    Calculates a commission for a transaction based on a per
    share cost with an optional minimum cost per trade.
    """

    def __init__(self, cost=0.03, min_trade_cost=None):
        """
        Cost parameter is the cost of a trade per-share. $0.03
        means three cents per share, which is a very conservative
        (quite high) for per share costs.
        min_trade_cost parameter is the minimum trade cost
        regardless of the number of shares traded (e.g. $1.00).
        """
        self.cost = float(cost)
        self.min_trade_cost = None if min_trade_cost is None\
            else float(min_trade_cost)

    def __repr__(self):
        return "{class_name}(cost={cost}, min trade cost={min_trade_cost})"\
            .format(class_name=self.__class__.__name__,
                    cost=self.cost,
                    min_trade_cost=self.min_trade_cost)

    def calculate(self, transaction):
        """
        returns a tuple of:
        (per share commission, total transaction commission)
        """
        commission = abs(transaction.amount * self.cost)
        if self.min_trade_cost is None:
            return self.cost, commission
        else:
            commission = max(commission, self.min_trade_cost)
            return abs(commission / transaction.amount), commission

    def __getstate__(self):

        state_dict = \
            {k: v for k, v in iteritems(self.__dict__)
                if not k.startswith('_')}

        STATE_VERSION = 1
        state_dict[VERSION_LABEL] = STATE_VERSION

        return state_dict

    def __setstate__(self, state):

        OLDEST_SUPPORTED_STATE = 1
        version = state.pop(VERSION_LABEL)

        if version < OLDEST_SUPPORTED_STATE:
            raise BaseException("PerShare saved state is too old.")

        self.__dict__.update(state)


# the commission of order
class OrderCost(object):
    """
    Calculates a commission for a transaction based on a per
    trade cost.
    """

    def __init__(self, open_tax=0,close_tax=0.001,open_commission=0.003,close_commission=0.003,close_today_commission=0,min_commission=5):
        """
        Cost parameter is the cost of a trade, regardless of
        share count. $5.00 per trade is fairly typical of
        discount brokers.
        """
        # Cost needs to be floating point so that calculation using division
        # logic does not floor to an integer.

        self.open_tax=open_tax
        self.close_tax=close_tax
        self.open_commission=open_commission
        self.close_commission=close_commission
        self.close_today_commission=close_today_commission
        self.min_commission=min_commission


    def calculate(self, transaction):
        """
        returns a tuple of:
        (per share commission, total transaction commission)
        """
        if transaction.amount == 0:
            return 0.0,0.0
        if transaction.amount > 0:
            return transaction.price*(self.open_commission), transaction.price*(self.open_commission)*transaction.amount
        else:
            return transaction.price*(self.close_commission+self.close_tax),transaction.price*(self.close_commission+self.close_tax)*abs(transaction.amount)


    def __getstate__(self):

        state_dict = \
            {k: v for k, v in iteritems(self.__dict__)
                if not k.startswith('_')}

        STATE_VERSION = 1
        state_dict[VERSION_LABEL] = STATE_VERSION

        return state_dict

    def __setstate__(self, state):

        OLDEST_SUPPORTED_STATE = 1
        version = state.pop(VERSION_LABEL)

        if version < OLDEST_SUPPORTED_STATE:
            raise BaseException("PerTrade saved state is too old.")

        self.__dict__.update(state)





class PerTrade(object):
    """
    Calculates a commission for a transaction based on a per
    trade cost.
    """

    def __init__(self, cost=5.0):
        """
        Cost parameter is the cost of a trade, regardless of
        share count. $5.00 per trade is fairly typical of
        discount brokers.
        """
        # Cost needs to be floating point so that calculation using division
        # logic does not floor to an integer.
        self.cost = float(cost)

    def calculate(self, transaction):
        """
        returns a tuple of:
        (per share commission, total transaction commission)
        """
        if transaction.amount == 0:
            return 0.0, 0.0

        return abs(self.cost / transaction.amount), self.cost

    def __getstate__(self):

        state_dict = \
            {k: v for k, v in iteritems(self.__dict__)
                if not k.startswith('_')}

        STATE_VERSION = 1
        state_dict[VERSION_LABEL] = STATE_VERSION

        return state_dict

    def __setstate__(self, state):

        OLDEST_SUPPORTED_STATE = 1
        version = state.pop(VERSION_LABEL)

        if version < OLDEST_SUPPORTED_STATE:
            raise BaseException("PerTrade saved state is too old.")

        self.__dict__.update(state)


class PerDollar(object):
    """
    Calculates a commission for a transaction based on a per
    dollar cost.
    """

    def __init__(self, cost=0.0015):
        """
        Cost parameter is the cost of a trade per-dollar. 0.0015
        on $1 million means $1,500 commission (=1,000,000 x 0.0015)
        """
        self.cost = float(cost)

    def __repr__(self):
        return "{class_name}(cost={cost})".format(
            class_name=self.__class__.__name__,
            cost=self.cost)

    def calculate(self, transaction):
        """
        returns a tuple of:
        (per share commission, total transaction commission)
        """
        cost_per_share = transaction.price * self.cost
        return cost_per_share, abs(transaction.amount) * cost_per_share

    def __getstate__(self):

        state_dict = \
            {k: v for k, v in iteritems(self.__dict__)
                if not k.startswith('_')}

        STATE_VERSION = 1
        state_dict[VERSION_LABEL] = STATE_VERSION

        return state_dict

    def __setstate__(self, state):

        OLDEST_SUPPORTED_STATE = 1
        version = state.pop(VERSION_LABEL)

        if version < OLDEST_SUPPORTED_STATE:
            raise BaseException("PerDollar saved state is too old.")

        self.__dict__.update(state)

"""
 FindMyOrder Main
"""
import logging
from datetime import datetime

import emoji
from pyparsing import (
    Combine, Optional, Word, alphas,
    nums, one_of, ParseBaseException,
    pyparsing_common, Suppress)

from .config import settings


class FindMyOrder:
    """find an order class """

    def __init__(
        self,
    ):
        self.logger = logging.getLogger(name="FMO")

    async def search(
        self,
        mystring: str,
    ) -> bool:
        """Search an order."""
        try:
            if mystring:
                string_check = mystring.split()[0]
                logging.debug("action identifier %s",
                              settings.action_identifier)
                if string_check.lower() in settings.action_identifier.lower():
                    logging.debug("found order in %s ", mystring)
                    return True
            logging.debug("no order found")
            return False
        except Exception:
            return False

    async def contains_emoji(self, s: str) -> bool:
        """Check if the input string contains an emoji."""
        return any(character in emoji.UNICODE_EMOJI_ENGLISH for character in s)

    async def is_match(self, grammar, s: str) -> bool:
        """Check if the input string matches the given grammar."""
        try:
            grammar.parseString(s, parseAll=True)
            return True
        except ParseBaseException:
            return False

    async def identify_order(
            self,
            mystring: str,
            ) -> dict:
        """Identify an order."""
        logging.debug("identify_order: %s", mystring)
        try:
            action = one_of(
                settings.action_identifier, caseless=True
                ).set_results_name("action").set_parse_action(
                    pyparsing_common.upcase_tokens)
            instrument = Word(
                alphas
                ).set_results_name("instrument")
            stop_loss = Combine(
                    Suppress(settings.stop_loss_identifier)
                    + Word(nums)
                ).set_results_name("stop_loss")
            take_profit = Combine(
                Suppress(settings.take_profit_identifier)
                + Word(nums)
                ).set_results_name("take_profit")
            quantity = Combine(
                Suppress(settings.quantity_identifier)
                + Word(nums)
                + Optional(Suppress("%"))
                ).set_results_name("quantity")
            order_type = one_of(
                settings.order_type_identifier, caseless=True
                ).set_results_name("order_type")
            leverage_type = one_of(
                settings.leverage_type_identifier, caseless=True
                ).set_results_name("leverage_type")
            comment = Combine(
                    Suppress(settings.comment_identifier)
                    + Word(alphas)
                ).set_results_name("comment")

            # for action in settings.actions:
            # print(f"{action.identifier} ({action.type})")
            order_grammar = (
                action("action")
                + Optional(instrument, default=None)
                + Optional(stop_loss, default=settings.stop_loss)
                + Optional(take_profit, default=settings.take_profit)
                + Optional(quantity, default=settings.quantity)
                + Optional(order_type, default=None)
                + Optional(leverage_type, default=None)
                + Optional(comment, default=None)
              )

            order = order_grammar.parse_string(
                    instring=mystring,
                    parse_all=False
                    )
            logging.debug("identify_order %s", order)
            # logging.info("identify_order:  %s", order.asDict())
            return order.asDict()

        except Exception as e:
            logging.exception("IdentifyError: %s", e)
            return None

    async def get_order(
        self,
        msg: str,
    ):
        """get an order."""
        try:
            logging.debug("get_order %s", msg)

            if await self.search(msg):
                logging.debug("get_order found in %s", msg)
                order = await self.identify_order(msg)
                logging.debug("order: %s", order)
                if isinstance(order, dict):
                    order["timestamp"] = datetime.utcnow().strftime(
                        "%Y-%m-%dT%H:%M:%SZ")
                return order
            return None

        except Exception as e:
            logging.exception("GetOrderError: %s", e)
            return None


# Grammar
# class TradingGrammar:
#     def __init__(self):
#         self.action = self._action()
#         self.instrument = self._instrument()
#         self.exchange = self._exchange()

# grammar = TradingGrammar()

# new_order_grammar = (
#     grammar.currency_pair
#     + grammar.exchange
#     + grammar.take_profit_targets
# )
# CORNIX type
# currency_pair = Combine(Suppress("#") + Word(alphas + "/") + Word(alphas))\
#     .set_results_name("currency_pair")
# exchange = Group(Suppress("Exchanges:")
# + delimitedList(
    # Word(alphas + " "),
    # delim=", ")
    # ).set_results_name("exchanges")
# signal_type = Group(
    # Suppress("Signal Type:")
    # + Word(alphas + " ()"))
#     .set_results_name("signal_type")
# leverage = Group(
    # Suppress("Leverage:")
    # + Word(alphas + " (.)"))\
#     .set_results_name("leverage")
# entry_targets = Group(Suppress("Entry Targets:")
# + OneOrMore(Group(Word(nums
# + ".")
# + Suppress("-")
# + Word(nums + ".%")))).set_results_name("entry_targets")
# take_profit_targets = Group(
    # Suppress("Take-Profit Targets:")
    # + OneOrMore(Word(nums + "."))).set_results_name("take_profit_targets")
# stop_targets = Group(
    # Suppress("Stop Targets:")
    # + OneOrMore(Word(nums + "."))).set_results_name("stop_targets")
# trailing_config = Group(
    # Suppress("Trailing Configuration:")
    # + Group(Word(alphas + ":")
    # + Word(alphas + "-")
    # + Suppress("Trigger:")
    # + Word(alphas + " ()"))).set_results_name("trailing_config")

# new_order_grammar = (
#     currency_pair
#     + exchange
#     + signal_type
#     + leverage
#     + entry_targets
#     + take_profit_targets
#     + stop_targets
#     + trailing_config
# )

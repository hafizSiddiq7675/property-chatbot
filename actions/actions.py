
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, Restarted
import os

class ActionValidateSalesPrice(Action):
    def name(self) -> Text:
        return "action_validate_sales_price"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        sales_price = next(tracker.get_latest_entity_values("amount"), None)
        if not sales_price:
            dispatcher.utter_message(text="I didn't understand the sales price. Please provide a number.")
            return []

        sales_price = float(sales_price)
        if sales_price < 50000:
            dispatcher.utter_message(text=f"🟡 YELLOW - Minimum Property Value - Low price reduces exit options (${sales_price:,.0f}).")
        else:
            dispatcher.utter_message(text=f"🟢 GREEN - Sales Price is acceptable (${sales_price:,.0f}).")

        # Ask for down payment
        dispatcher.utter_message(text="Next, what's your down payment?")

        return [SlotSet("sales_price", sales_price)]

class ActionValidateDownPayment(Action):
    def name(self) -> Text:
        return "action_validate_down_payment"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        down_payment = next(tracker.get_latest_entity_values("amount"), None)
        sales_price = tracker.get_slot("sales_price")

        if not down_payment:
            dispatcher.utter_message(text="I didn't understand the down payment. Please provide a number.")
            return []

        if not sales_price:
            dispatcher.utter_message(text="I don't have the sales price yet. Please provide the sales price first.")
            return []

        # Convert to float (in case they're strings)
        down_payment = float(down_payment)
        sales_price = float(sales_price)
        down_payment_pct = (down_payment / sales_price) * 100

        if down_payment_pct < 10:
            dispatcher.utter_message(text=f"🟡 YELLOW - Minimum Down Payment - Target at least 10% ({down_payment_pct:.1f}% down).")
        elif 10 <= down_payment_pct < 20:
            dispatcher.utter_message(text=f"🟡 YELLOW - Moderate Down Payment - Consider increasing to 20% ({down_payment_pct:.1f}% down).")
        else:
            dispatcher.utter_message(text=f"🟢 GREEN - Optimal Down Payment - {down_payment_pct:.1f}% down. Excellent equity position!")

        # Ask for interest rate
        dispatcher.utter_message(text="Now, what's the interest rate?")

        return [SlotSet("down_payment", down_payment)]

class ActionValidateInterestRate(Action):
    def name(self) -> Text:
        return "action_validate_interest_rate"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        interest_rate = next(tracker.get_latest_entity_values("rate"), None)
        if not interest_rate:
            dispatcher.utter_message(text="I didn't understand the interest rate. Please provide a percentage.")
            return []

        interest_rate = float(str(interest_rate).replace("%", ""))
        bank_rate = float(os.environ.get("BANK_RATE", 6.5))

        if interest_rate < (bank_rate + 2):
            dispatcher.utter_message(text=f"🟡 YELLOW - Minimum Interest Rate - Below market rate, verify details ({interest_rate:.2f}%).")
        elif interest_rate > 10:
            dispatcher.utter_message(text=f"🟡 YELLOW - Usury Warning - High rate, consider refinancing ({interest_rate:.2f}%).")
        else:
            dispatcher.utter_message(text=f"🟢 GREEN - Optimal Interest Rate - {interest_rate:.2f}% is competitive.")

        # Note: Summary will be triggered by the story flow

        return [SlotSet("interest_rate", interest_rate)]

class ActionShowSummary(Action):
    def name(self) -> Text:
        return "action_show_summary"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        sales_price = tracker.get_slot("sales_price")
        down_payment = tracker.get_slot("down_payment")
        interest_rate = tracker.get_slot("interest_rate")

        if not all([sales_price, down_payment, interest_rate]):
            dispatcher.utter_message(text="I'm missing some information. Please provide sales price, down payment, and interest rate.")
            return []

        # Convert to float (in case they're strings)
        sales_price = float(sales_price)
        down_payment = float(down_payment)
        interest_rate = float(interest_rate)

        loan_amount = sales_price - down_payment
        down_payment_pct = (down_payment / sales_price) * 100
        monthly_interest_rate = (interest_rate / 100) / 12
        number_of_payments = 30 * 12
        
        if monthly_interest_rate > 0:
            monthly_payment = loan_amount * (monthly_interest_rate * (1 + monthly_interest_rate) ** number_of_payments) / ((1 + monthly_interest_rate) ** number_of_payments - 1)
        else:
            monthly_payment = loan_amount / number_of_payments


        summary = (
            f"📊 Summary:\n"
            f"- Sales Price: ${sales_price:,.0f}\n"
            f"- Down Payment: ${down_payment:,.0f} ({down_payment_pct:.1f}%)\n"
            f"- Loan Amount: ${loan_amount:,.0f}\n"
            f"- Interest Rate: {interest_rate:.2f}%\n"
            f"- Monthly Payment: ~${monthly_payment:,.0f}\n\n"
            f"Type 'reset' to start a new calculation or 'hi' to begin again."
        )

        dispatcher.utter_message(text=summary)

        return []

class ActionReset(Action):
    def name(self) -> Text:
        return "action_reset"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Send the restart message
        dispatcher.utter_message(text='🔄 Starting fresh! and start with greeting "Hi".')

        # Reset all slots
        return [
            SlotSet("sales_price", None),
            SlotSet("down_payment", None),
            SlotSet("interest_rate", None),
            Restarted()
        ]
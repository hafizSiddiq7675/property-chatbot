
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, Restarted
from rasa_sdk.types import DomainDict
import os
import re


class ValidatePropertyForm(FormValidationAction):
    """Form validation action for property_form"""

    def name(self) -> Text:
        return "validate_property_form"

    def validate_zip_code(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate zip_code value."""

        if not slot_value:
            dispatcher.utter_message(text="I didn't understand the zip code. Please provide a 5-digit zip code.")
            return {"zip_code": None}

        # Validate zip code format
        zip_code = str(slot_value).strip()
        if not re.match(r'^\d{5}$', zip_code):
            dispatcher.utter_message(text="Please provide a valid 5-digit zip code.")
            return {"zip_code": None}

        # Send confirmation message
        dispatcher.utter_message(text=f"✅ Zip Code: {zip_code}")
        return {"zip_code": zip_code}

    def validate_property_state(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate property_state value."""

        if not slot_value:
            dispatcher.utter_message(text="I didn't understand the state. Please provide the state name or abbreviation.")
            return {"property_state": None}

        # Map state names to abbreviations
        state_mapping = {
            "california": "CA", "texas": "TX", "florida": "FL", "new york": "NY",
            "illinois": "IL", "georgia": "GA", "arizona": "AZ", "ohio": "OH",
            "pennsylvania": "PA", "north carolina": "NC", "michigan": "MI",
            "new jersey": "NJ", "virginia": "VA", "washington": "WA",
            "massachusetts": "MA", "indiana": "IN", "tennessee": "TN",
            "missouri": "MO", "maryland": "MD", "wisconsin": "WI",
            "minnesota": "MN", "colorado": "CO", "alabama": "AL",
            "south carolina": "SC", "louisiana": "LA", "kentucky": "KY",
            "oregon": "OR", "oklahoma": "OK", "connecticut": "CT",
            "iowa": "IA", "utah": "UT", "nevada": "NV", "arkansas": "AR",
            "mississippi": "MS", "kansas": "KS", "new mexico": "NM",
            "nebraska": "NE", "west virginia": "WV", "idaho": "ID",
            "hawaii": "HI", "new hampshire": "NH", "maine": "ME",
            "rhode island": "RI", "montana": "MT", "delaware": "DE",
            "south dakota": "SD", "north dakota": "ND", "alaska": "AK",
            "vermont": "VT", "wyoming": "WY"
        }

        state_str = str(slot_value).strip()
        state_lower = state_str.lower()

        # Convert to abbreviation if full name provided
        if state_lower in state_mapping:
            state_abbr = state_mapping[state_lower]
        elif len(state_str) == 2 and state_str.upper() in state_mapping.values():
            state_abbr = state_str.upper()
        else:
            state_abbr = state_str.upper()

        # Send confirmation message
        dispatcher.utter_message(text=f"✅ State: {state_abbr}")
        return {"property_state": state_abbr}

    def validate_sales_price(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate sales_price value."""

        if not slot_value:
            dispatcher.utter_message(text="I didn't understand the sales price. Please provide a number.")
            return {"sales_price": None}

        try:
            sales_price = float(slot_value)
        except (ValueError, TypeError):
            dispatcher.utter_message(text="Please provide a valid number for the sales price.")
            return {"sales_price": None}

        if sales_price < 50000:
            dispatcher.utter_message(text=f"Minimum Property Value - Low price reduces exit options (${sales_price:,.0f}).")
        else:
            dispatcher.utter_message(text=f"Sales Price is acceptable (${sales_price:,.0f}).")

        return {"sales_price": sales_price}

    def validate_down_payment(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate down_payment value."""

        if not slot_value:
            dispatcher.utter_message(text="I didn't understand the down payment. Please provide a number.")
            return {"down_payment": None}

        sales_price = tracker.get_slot("sales_price")

        if not sales_price:
            dispatcher.utter_message(text="I don't have the sales price yet. Please provide the sales price first.")
            return {"down_payment": None}

        try:
            down_payment = float(slot_value)
            sales_price = float(sales_price)
        except (ValueError, TypeError):
            dispatcher.utter_message(text="Please provide a valid number for the down payment.")
            return {"down_payment": None}

        down_payment_pct = (down_payment / sales_price) * 100

        if down_payment_pct < 10:
            dispatcher.utter_message(text=f"Minimum Down Payment - Target at least 10% ({down_payment_pct:.1f}% down).")
        elif 10 <= down_payment_pct < 20:
            dispatcher.utter_message(text=f"Moderate Down Payment - Consider increasing to 20% ({down_payment_pct:.1f}% down).")
        else:
            dispatcher.utter_message(text=f"Optimal Down Payment - {down_payment_pct:.1f}% down. Excellent equity position!")

        return {"down_payment": down_payment}

    def validate_interest_rate(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate interest_rate value."""

        if not slot_value:
            dispatcher.utter_message(text="I didn't understand the interest rate. Please provide a percentage.")
            return {"interest_rate": None}

        try:
            interest_rate = float(str(slot_value).replace("%", ""))
        except (ValueError, TypeError):
            dispatcher.utter_message(text="Please provide a valid number for the interest rate.")
            return {"interest_rate": None}

        bank_rate = float(os.environ.get("BANK_RATE", 6.5))

        if interest_rate < (bank_rate + 2):
            dispatcher.utter_message(text=f"Minimum Interest Rate - Below market rate, verify details ({interest_rate:.2f}%).")
        elif interest_rate > 10:
            dispatcher.utter_message(text=f"Usury Warning - High rate, consider refinancing ({interest_rate:.2f}%).")
        else:
            dispatcher.utter_message(text=f"Optimal Interest Rate - {interest_rate:.2f}% is competitive.")

        return {"interest_rate": interest_rate}

    def validate_occupancy_type(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate occupancy_type value."""

        if not slot_value:
            dispatcher.utter_message(text="I didn't understand the occupancy type. Please type 'owner' or 'non-owner'.")
            return {"occupancy_type": None}

        occupancy_str = str(slot_value).strip().lower()

        # Normalize occupancy type
        if "owner" in occupancy_str and "non" not in occupancy_str:
            occupancy_type = "owner-occupied"
            dispatcher.utter_message(text="Owner-Occupied property (typically lower risk)")
        else:
            occupancy_type = "non-owner-occupied"
            dispatcher.utter_message(text="Non-Owner-Occupied property (investment property)")

        return {"occupancy_type": occupancy_type}

    def validate_loan_term(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate loan_term value."""

        if not slot_value:
            dispatcher.utter_message(text="I didn't understand the loan term. Please provide the number of years.")
            return {"loan_term": None}

        try:
            loan_term = float(slot_value)
        except (ValueError, TypeError):
            dispatcher.utter_message(text="Please provide a valid number for the loan term.")
            return {"loan_term": None}

        # Validate loan term
        if loan_term < 5:
            dispatcher.utter_message(text=f"Loan Term: {int(loan_term)} years (short term, higher payments)")
        elif loan_term > 30:
            dispatcher.utter_message(text=f"Loan Term: {int(loan_term)} years (longer than standard 30-year term)")
        else:
            dispatcher.utter_message(text=f"Loan Term: {int(loan_term)} years (standard term)")

        return {"loan_term": loan_term}

    def validate_title_insurance(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate title_insurance value."""

        if not slot_value:
            dispatcher.utter_message(text="I didn't understand. Please type 'yes' or 'no' for title insurance.")
            return {"title_insurance": None}

        title_str = str(slot_value).strip().lower()

        # Normalize to yes/no
        if title_str in ["yes", "y", "title insurance", "lender's title insurance", "we have title insurance"]:
            title_insurance = "yes"
            dispatcher.utter_message(text="Lender's Title Insurance Policy: Yes (Good protection)")
        elif title_str in ["no", "n", "no title insurance"]:
            title_insurance = "no"
            dispatcher.utter_message(text="No Lender's Title Insurance - Consider obtaining coverage")
        else:
            title_insurance = title_str

        return {"title_insurance": title_insurance}

    def validate_property_type(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate property_type value."""

        if not slot_value:
            dispatcher.utter_message(text="I didn't understand the property type. Please choose: sfh, condo, townhouse, multi-family, mobile-home, or raw-land.")
            return {"property_type": None}

        # Map property types
        property_type_mapping = {
            "sfh": "Single Family Home",
            "single family home": "Single Family Home",
            "single family": "Single Family Home",
            "condo": "Condo",
            "condominium": "Condo",
            "townhouse": "Townhouse",
            "town house": "Townhouse",
            "multi-family": "Multi-Family (2-4 units)",
            "multi family": "Multi-Family (2-4 units)",
            "multifamily": "Multi-Family (2-4 units)",
            "mobile-home": "Mobile Home",
            "mobile home": "Mobile Home",
            "mobile": "Mobile Home",
            "raw-land": "Raw Land",
            "raw land": "Raw Land",
            "land": "Raw Land"
        }

        property_str = str(slot_value).strip().lower()

        if property_str in property_type_mapping:
            property_type = property_type_mapping[property_str]

            # Provide feedback based on property type
            if property_str in ["sfh", "single family home", "single family"]:
                dispatcher.utter_message(text=f"Property Type: {property_type} (Most marketable)")
            elif property_str in ["condo", "condominium", "townhouse", "town house"]:
                dispatcher.utter_message(text=f"Property Type: {property_type} (Good marketability)")
            elif property_str in ["multi-family", "multi family", "multifamily"]:
                dispatcher.utter_message(text=f"Property Type: {property_type} (Investment property)")
            elif property_str in ["mobile-home", "mobile home", "mobile"]:
                dispatcher.utter_message(text=f"Property Type: {property_type} (Verify if permanently attached)")
            elif property_str in ["raw-land", "raw land", "land"]:
                dispatcher.utter_message(text=f"Property Type: {property_type} (Higher risk - no improvements)")
            else:
                dispatcher.utter_message(text=f"Property Type: {property_type}")
        else:
            dispatcher.utter_message(text="I didn't recognize that property type. Please choose: sfh, condo, townhouse, multi-family, mobile-home, or raw-land.")
            return {"property_type": None}

        return {"property_type": property_type}


class ActionShowSummary(Action):
    def name(self) -> Text:
        return "action_show_summary"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Get all slots
        zip_code = tracker.get_slot("zip_code")
        property_state = tracker.get_slot("property_state")
        sales_price = tracker.get_slot("sales_price")
        down_payment = tracker.get_slot("down_payment")
        interest_rate = tracker.get_slot("interest_rate")
        occupancy_type = tracker.get_slot("occupancy_type")
        loan_term = tracker.get_slot("loan_term")
        title_insurance = tracker.get_slot("title_insurance")
        property_type = tracker.get_slot("property_type")

        # Check if we have all required information
        if not all([sales_price, down_payment, interest_rate]):
            dispatcher.utter_message(text="I'm missing some information. Please provide sales price, down payment, and interest rate.")
            return []

        # Convert to float (in case they're strings)
        sales_price = float(sales_price)
        down_payment = float(down_payment)
        interest_rate = float(interest_rate)
        loan_term = float(loan_term) if loan_term else 30

        # Calculate loan details
        loan_amount = sales_price - down_payment
        down_payment_pct = (down_payment / sales_price) * 100
        monthly_interest_rate = (interest_rate / 100) / 12
        number_of_payments = int(loan_term * 12)

        # Calculate monthly payment
        if monthly_interest_rate > 0:
            monthly_payment = loan_amount * (monthly_interest_rate * (1 + monthly_interest_rate) ** number_of_payments) / ((1 + monthly_interest_rate) ** number_of_payments - 1)
        else:
            monthly_payment = loan_amount / number_of_payments

        # Build the summary message with proper formatting
        summary = f"""📊 Property Investment Summary:

📍 Location:
   • Zip Code: {zip_code if zip_code else 'N/A'}
   • State: {property_state if property_state else 'N/A'}

🏠 Property Details:
   • Property Type: {property_type if property_type else 'N/A'}
   • Occupancy: {occupancy_type if occupancy_type else 'N/A'}
   • Lender's Title Insurance: {title_insurance.title() if title_insurance else 'N/A'}

💰 Financial Details:
   • Sales Price: ${sales_price:,.0f}
   • Down Payment: ${down_payment:,.0f} ({down_payment_pct:.1f}%)
   • Loan Amount: ${loan_amount:,.0f}
   • Interest Rate: {interest_rate:.2f}%
   • Loan Term: {int(loan_term)} years
   • Monthly Payment: ~${monthly_payment:,.0f}

💡 Need a full detailed validation? Contact us for complete analysis.

Type 'reset' to start a new calculation or 'hi' to begin again."""

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
            SlotSet("zip_code", None),
            SlotSet("property_state", None),
            SlotSet("sales_price", None),
            SlotSet("down_payment", None),
            SlotSet("interest_rate", None),
            SlotSet("occupancy_type", None),
            SlotSet("loan_term", None),
            SlotSet("title_insurance", None),
            SlotSet("property_type", None),
            Restarted()
        ]

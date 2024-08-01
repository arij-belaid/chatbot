from typing import Any, Text, Dict, List

import couchdb
from rasa_sdk import Action, Tracker, logger
from rasa_sdk.executor import CollectingDispatcher
import logging

logger = logging.getLogger(__name__)
from transformers import GPT2LMHeadModel, GPT2Tokenizer
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher


class ActionHelloWorld(Action):

    def name(self) -> Text:
        return "action_hello_world"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(text="Hello World!")

        return []
class ActionSaveConversation(Action):
    def name(self) -> str:
        return "action_save_conversation"

    def __init__(self):
        try:
            self.couchdb_server = couchdb.Server("http://localhost:5984/")
            self.db = self.couchdb_server["conversations"]
            logger.info("Successfully connected to CouchDB.")
        except Exception as e:
            logger.error(f"Failed to connect to CouchDB: {e}")
            self.db = None

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: dict) -> list:
        if not self.db:
            dispatcher.utter_message(text="Failed to connect to the database.")
            return []

        try:
            events = tracker.events
            conversation = []
            bot_question = None

            # Build the conversation list
            for event in events:
                if event["event"] == "bot":
                    # Update the last bot question
                    bot_question = event.get("text", "")
                elif event["event"] == "user":
                    # Add the bot question and response to the conversation list
                    if bot_question:
                        conversation.append({bot_question: event.get("text", "")})
                        bot_question = None

            # Save the conversation to CouchDB
            conversation = {
                    "conversation": conversation
                }
           # Save conversation to CouchDB
            self.db.save(conversation)
            dispatcher.utter_message(text="Conversation saved successfully.")
            logger.info("Conversation saved successfully.")
        except Exception as e:
            logger.error(f"Failed to save conversation: {e}")
            dispatcher.utter_message(text="Failed to save conversation.")

        return []
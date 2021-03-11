# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List, Union

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from rasa_sdk.forms import FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import (
    SlotSet,
    UserUtteranceReverted,
    ConversationPaused,
    EventType,
    FollowupAction,
    AllSlotsReset
)

from rasa_sdk.types import DomainDict

import os
import sys
import requests
import time
import logging
import tqdm

import pymongo
import json
import getopt, pprint

import pandas as pd
import numpy as np
import uuid

class ActionResetAllSlots(Action):

    def name(self):
        return "action_reset_all_slots"

    def run(self, dispatcher, tracker, domain):
        return [AllSlotsReset()]

class ValidateLoginForm(Action):
    def name(self) -> Text:
        return "login_form"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        required_slots = ["EMP_ID","password"]

        for slot_name in required_slots:
            if tracker.slots.get(slot_name) is None:
                # The slot is not filled yet. Request the user to fill this slot next.
                return [SlotSet("requested_slot", slot_name)]
                
        # myclient = pymongo.MongoClient('mongodb://192.168.1.104:27017/')
        # db = myclient['EMP-DB']
        # collection_name = 'Employee_DB'
        # col = db[collection_name]
        # emp_id = tracker.get_slot("EMP_ID")

        # try:
        #     emp_data = col.find({'_id':emp_id})[0]
        #     password = emp_data['password']
        #     if password==tracker.get_slot('password'):
        #         dispatcher.utter_message(template="utter_logged_in")
        #         # print("inside run function of login form; login success")
        #         # All slots are filled.
        #         return [SlotSet("requested_slot", None)]
        #     else:
        #         dispatcher.utter_message(template="utter_invalid_password")
        #         # print("inside run function of login form; invalid password")
        #         return [SlotSet("password", None)]

        # except:
        #     logging.info(f'Data not available for Employee {emp_id}, Invalid User! Contact Admin')
        #     dispatcher.utter_message(template="utter_no_data_available",
        #                          Employee_ID=emp_id,
        #                          )

class ActionSubmitLogInForm(Action):
    def name(self) -> Text:
        return "action_submit_login_form"

    def run(
        self,
        dispatcher,
        tracker: Tracker,
        domain: "DomainDict",
    ) -> List[Dict[Text, Any]]:
        myclient = pymongo.MongoClient('mongodb://192.168.1.104:27017/')
        db = myclient['EMP-DB']
        collection_name = 'Employee_DB'
        col = db[collection_name]
        emp_id = tracker.get_slot("EMP_ID")
        try:
            emp_data = col.find({'_id':emp_id})[0]
            password = emp_data['password']
            if password==tracker.get_slot('password'):
                dispatcher.utter_message(template="utter_logged_in")
                # print("success; inside run function of the submit form class")
            else:
                dispatcher.utter_message(template="utter_invalid_password")
                # print("invalid password; inside run function of the submit form class")
                # return [SlotSet("password", None)]
        except:
            logging.info(f'Data not available for Employee {emp_id}, Invalid User! Contact Admin')
            dispatcher.utter_message(template="utter_no_data_available",
                                 Employee_ID=emp_id,
                                 )

class ActionApplyForReimbursement(Action):
    def name(self) -> Text:
        return "action_submit_apply_for_reimbursement"

    def run(
        self,
        dispatcher,
        tracker: Tracker,
        domain: "DomainDict",
    ) -> List[Dict[Text, Any]]:

        myclient = pymongo.MongoClient('mongodb://192.168.1.104:27017/')
        db = myclient['EMP-DB']
        col = db["Employee_DB"]

        amount = int(tracker.get_slot("amount"))
        reimbursement_type = tracker.get_slot("reimbursement_type")
        emp_id = tracker.get_slot("EMP_ID")

        emp_data = col.find({'_id':emp_id})[0]
        manager = emp_data['Manager']

        request_col = db["Request_DB"]
        try:
            probably_unique_R = "-".join([str(pd.to_datetime("now")),emp_id,reimbursement_type,str(amount)])
            SHA1_ID_R = str(uuid.uuid5(uuid.NAMESPACE_URL,probably_unique_R))
            # ref -- https://docs.python.org/3/library/uuid.html

            insert = {
                "_id":SHA1_ID_R,
                "datetime" : pd.to_datetime("now"),
                "EMP_ID" : emp_id,
                "Manager" : manager,
                "Request_Type": f"reimbursement_request - {reimbursement_type}",
                "Request_Status" : "Opened",
                "Remarks" : f"{reimbursement_type} reimbursement request of {amount}"
            }
            request_col.insert_one(insert)
            dispatcher.utter_message(template="utter_reimbursement_request_upload_doc",
                                    request_id=SHA1_ID_R)
            
        except:
            logging.info(f'Data not available for Employee {emp_id}')
            dispatcher.utter_message(template="utter_no_data_available",
                                 Employee_ID=emp_id,
                                 )

class ActionApplyForLeave(Action):
    def name(self) -> Text:
        return "action_apply_for_leave"

    def run(
        self,
        dispatcher,
        tracker: Tracker,
        domain: "DomainDict",
    ) -> List[Dict[Text, Any]]:

        myclient = pymongo.MongoClient('mongodb://192.168.1.104:27017/')
        db = myclient['EMP-DB']
        col = db["Employee_DB"]

        no_of_days = int(tracker.get_slot("no_of_days"))
        start_date = tracker.get_slot("start_date")
        end_date = tracker.get_slot("end_date")
        emp_id = tracker.get_slot("EMP_ID")

        emp_data = col.find({'_id':emp_id})[0]
        manager = emp_data['Manager']

        request_col = db["Request_DB"]
        try:
            leaves_left = int(emp_data['leaves_cap'] - emp_data['leaves_taken'])

            if leaves_left>=no_of_days:
                probably_unique = "-".join([str(pd.to_datetime("now")),emp_id,start_date,end_date,str(no_of_days)])
                SHA1_ID = str(uuid.uuid5(uuid.NAMESPACE_URL,probably_unique))
                # ref -- https://docs.python.org/3/library/uuid.html

                insert = {
                    "_id":SHA1_ID,
                    "datetime" : pd.to_datetime("now"),
                    "EMP_ID" : emp_id,
                    "Manager" : manager,
                    "Request_Type": "leave_request",
                    "Request_Status" : "Opened",
                    "Remarks" : f"Leave request for {no_of_days} days. Start Date - {start_date}, End date - {end_date}"
                }
                request_col.insert_one(insert)
                dispatcher.utter_message(template="utter_leave_request_submitted",
                                        request_id=SHA1_ID)

                # update the Employee DB 
                new_leave_taken = int(emp_data['leaves_taken'])+no_of_days
                myquery = { "_id": emp_id }
                newvalues = { "$set": { "leaves_taken":new_leave_taken} }
                col.update_one(myquery, newvalues)

            else:
                dispatcher.utter_message(template="utter_no_leaves_available")

        except:
            logging.info(f'Data not available for Employee {emp_id}')
            dispatcher.utter_message(template="utter_no_data_available",
                                 Employee_ID=emp_id,
                                 )

class ActionSubmitLeaveBalance(Action):
    def name(self) -> Text:
        return "action_submit_leave_balance_form"

    def run(
        self,
        dispatcher,
        tracker: Tracker,
        domain: "DomainDict",
    ) -> List[Dict[Text, Any]]:
        myclient = pymongo.MongoClient('mongodb://192.168.1.104:27017/')
        db = myclient['EMP-DB']
        collection_name = 'Employee_DB'
        col = db[collection_name]
        emp_id = tracker.get_slot("EMP_ID")

        try:
            emp_data = col.find({'_id':emp_id})[0]
            password = emp_data['password']
            if password==tracker.get_slot('password'):
                leaves_left = emp_data['leaves_cap'] - emp_data['leaves_taken']
                dispatcher.utter_message(template="utter_leave_balance",
                                        Employee_ID=emp_id,
                                        Leaves_Left=leaves_left
                                        )
            else:
                dispatcher.utter_message(template="utter_invalid_password")
        except:
            logging.info(f'Data not available for Employee {emp_id}')
            dispatcher.utter_message(template="utter_no_data_available",
                                 Employee_ID=emp_id,
                                 )

class ActionSubmitPTO(Action):
    def name(self) -> Text:
        return "action_submit_pto_balance_form"

    def run(
        self,
        dispatcher,
        tracker: Tracker,
        domain: "DomainDict",
    ) -> List[Dict[Text, Any]]:
        myclient = pymongo.MongoClient('mongodb://192.168.1.104:27017/')
        db = myclient['EMP-DB']
        collection_name = 'Employee_DB'
        col = db[collection_name]
        emp_id = tracker.get_slot("EMP_ID")
        try:
            emp_data = col.find({'_id':emp_id})[0]
            password = emp_data['password']
            if password==tracker.get_slot('password'):
                pto_left = emp_data['PTO_Cap'] - emp_data['PTO_Taken']
                dispatcher.utter_message(template="utter_pto_balance",
                                        Employee_ID=emp_id,
                                        PTO_Left=pto_left
                                        )
            else:
                dispatcher.utter_message(template="utter_invalid_password")

        except:
            logging.info(f'Data not available for Employee {emp_id}')
            dispatcher.utter_message(template="utter_no_data_available",
                                 Employee_ID=emp_id,
                                 )
               
class ActionSubmitFetchPayslip(Action):
    def name(self) -> Text:
        return "action_submit_fetch_payslip_form"

    def run(
        self,
        dispatcher,
        tracker: Tracker,
        domain: "DomainDict",
    ) -> List[Dict[Text, Any]]:
        myclient = pymongo.MongoClient('mongodb://192.168.1.104:27017/')
        db = myclient['EMP-DB']
        collection_name = 'Employee_DB'
        col = db[collection_name]
        emp_id = tracker.get_slot("EMP_ID")
        try:
            emp_data = col.find({'_id':emp_id})[0]
            password = emp_data['password']
            if password==tracker.get_slot('password'):
                payslip = emp_data['Payslip']
                dispatcher.utter_message(template="utter_payslip_link",
                                        Payslip=payslip,
                                        )
            else:
                dispatcher.utter_message(template="utter_invalid_password")

        except:
            logging.info(f'Data not available for Employee {emp_id}')
            dispatcher.utter_message(template="utter_no_data_available",
                                 Employee_ID=emp_id,
                                 )
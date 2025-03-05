

import frappe
from frappe.model.document import Document


class RavenNotification(Document):
	pass
# Copyright (c) 2018, Frappe Technologies and contributors
# License: MIT. See LICENSE

import json
import os
from collections import namedtuple

import frappe
from frappe import _
from frappe.core.doctype.role.role import get_info_based_on_role, get_user_info
from frappe.core.doctype.sms_settings.sms_settings import send_sms
from frappe.desk.doctype.notification_log.notification_log import enqueue_create_notification
from frappe.integrations.doctype.slack_webhook_url.slack_webhook_url import send_slack_message
from frappe.model.document import Document
from frappe.modules.utils import export_module_json, get_doc_module
from frappe.utils import add_to_date, cast, nowdate, validate_email_address
from frappe.utils.jinja import validate_template
from frappe.utils.safe_exec import get_safe_globals

from frappe.utils import get_site_url

import frappe
from frappe.model.document import Document
from jinja2 import Template

import frappe
from frappe.utils.print_format import download_pdf

import os
import frappe
from frappe.utils.pdf import get_pdf



# This function is calling in hooks for send message to raven
def send_a_raven(doc, method):
    
    try:
        if not doc or not doc.doctype:
            frappe.msgprint("Invalid input parameters")
            return
        
        # Fetch relevant Raven channels based on document type and method    
        raven_channel = get_raven_channel(doc.doctype,method)
        

        if raven_channel:
            for raven_notification_dict in raven_channel:
                # Check if there is a condition set for the notification
                condition = raven_notification_dict.get("condition")
                need_approval_button = raven_notification_dict.get("need_approval_button")
                
                if condition:
                    # Evaluate the condition to determine if the notification should be sent
                    if eval(condition):
                        if raven_notification_dict.get("raven_channel"):
                            # Loop through each channel name and fetch Raven channels that are not direct messages
                            for channel_name in raven_notification_dict.get("raven_channel"):
                                channels = frappe.get_all("Raven Channel", filters={"name": channel_name}, fields=["name", "channel_name", "is_direct_message"])
                                
                                if channels and channels[0].get("is_direct_message") == 0:
                                    selected_channel = channels[0].get("name")
                                    raven_message = raven_channel[0].get("message")
                                    rendered_message = render_message_template(raven_message, doc)
                                    if raven_channel[0].get("json"):
                                        json_data = get_data_from_json(doc,raven_channel[0].get("json"))
                                    else:
                                        json_data = '{}'
                                    link = raven_channel[0].get("link")
                                    # Set subject for the message, if available
                                    if raven_notification_dict.get("subject"):
                                        subject =  raven_notification_dict.get("subject")
                                    else:
                                        subject = ''
                                    # this is for pdf generation
                                    # pdf_link = raven_channel[0].get("pdf_link")

                                    # get_pdf(doc.doctype, doc.name, raven_channel[0].get("print_format"), doc=None, no_letterhead=0, language=None, letterhead=None)
                                    # pdf_url = generate_pdf_from_doc("Sales Invoice", "ACC-SINV-2024-00003", raven_channel[0].get("print_format"), doc=doc)

                                    # pdf_url = generate_pdf_from_doc(doc, print_format=raven_channel[0].get("print_format"),no_letterhead=0)

                                    # Create and send the Raven message
                                    create_and_send_raven_message(doc,subject ,selected_channel, rendered_message,json_data,link,need_approval_button)
                                else:
                                    frappe.msgprint("No channels found")
                        else:
                            # Handle direct messages (DM)
                            if raven_notification_dict.get("dm"):
                                for raven_users in raven_notification_dict.get("dm"):
                                   
                                    # channels = frappe.get_all("Raven Channel", filters={"name": channel_name}, fields=["name", "channel_name", "is_direct_message"])

                                    # Construct DM channel name using the admin email and user
                                    admin_email = 'admin@example.com'
                                    channel_name = f"{admin_email} _ {raven_users}"
                                    # Fetch or create a direct message channel
                                    channel_id = frappe.db.get_value('Raven Channel', 
                                        {
                                            "channel_name": channel_name,
                                            "is_direct_message": 1
                                        }, 
                                        'name'
                                    )
                                    
                                    if not channel_id:
                                        # Create a new Raven Channel for direct messages
                                        channel_doc = frappe.new_doc('Raven Channel')
                                        channel_doc.channel_name = channel_name
                                        channel_doc.is_direct_message = True
                                        channel_doc.is_self_message = False  # Admin is not messaging themselves
                                        channel_doc.save()
                                        frappe.db.commit()
                                        channel_id = channel_doc.name
                                        print(f"Created new Raven Channel with ID: {channel_id}")
                                    else:
                                        print(f"Fetched existing Raven Channel with ID: {channel_id}")
                                    
                                    # Create and send Raven Message
                                    if channel_id:
                                       
                                        selected_channel = channel_id
                                        raven_message = raven_channel[0].get("message")
                                        rendered_message = render_message_template(raven_message, doc)
                                        if raven_channel[0].get("json"):
                                            json_data = get_data_from_json(doc,raven_channel[0].get("json"))
                                        else:
                                            json_data = '{}'
                                        link = raven_channel[0].get("link")

                                        if raven_notification_dict.get("subject"):
                                            subject =  raven_notification_dict.get("subject")
                                        else:
                                            subject = ''
                                        # this is for pdf generation
                                        # pdf_link = raven_channel[0].get("pdf_link")

                                        # get_pdf(doc.doctype, doc.name, raven_channel[0].get("print_format"), doc=None, no_letterhead=0, language=None, letterhead=None)
                                        # pdf_url = generate_pdf_from_doc("Sales Invoice", "ACC-SINV-2024-00003", raven_channel[0].get("print_format"), doc=doc)

                                        # pdf_url = generate_pdf_from_doc(doc, print_format=raven_channel[0].get("print_format"),no_letterhead=0)

                                        # Create and send the Raven message
                                        create_and_send_raven_message(doc, subject,selected_channel, rendered_message,json_data,link,need_approval_button)
                                        print(f"Created new Raven Message linked to Channel ID: {channel_id}")
                                    else:
                                        print(f"Cannot create Raven Message; no valid Channel ID found.")
                else:
                    # Handle case when no condition is set
                    if raven_notification_dict.get("raven_channel"):
                        # Loop through each channel name and fetch Raven channels that are not direct messages
                        for channel_name in raven_notification_dict.get("raven_channel"):
                            channels = frappe.get_all("Raven Channel", filters={"name": channel_name}, fields=["name", "channel_name", "is_direct_message"])
                            
                            if channels and channels[0].get("is_direct_message") == 0:
                                selected_channel = channels[0].get("name")
                                raven_message = raven_channel[0].get("message")
                                rendered_message = render_message_template(raven_message, doc)
                                if raven_channel[0].get("json"):
                                    json_data = get_data_from_json(doc,raven_channel[0].get("json"))
                                else:
                                    json_data = '{}'
                                link = raven_channel[0].get("link")
                                if raven_notification_dict.get("subject"):
                                    subject =  raven_notification_dict.get("subject")
                                else:
                                    subject = ''
                                # this is for pdf generation
                                # pdf_link = raven_channel[0].get("pdf_link")

                                # get_pdf(doc.doctype, doc.name, raven_channel[0].get("print_format"), doc=None, no_letterhead=0, language=None, letterhead=None)
                                # pdf_url = generate_pdf_from_doc("Sales Invoice", "ACC-SINV-2024-00003", raven_channel[0].get("print_format"), doc=doc)

                                # pdf_url = generate_pdf_from_doc(doc, print_format=raven_channel[0].get("print_format"),no_letterhead=0)


                                create_and_send_raven_message(doc, subject,selected_channel, rendered_message,json_data,link,need_approval_button)
                            else:
                                frappe.msgprint("No channels found")
                    else:
                        # Handle direct messages (DM) when no condition is set
                        if raven_notification_dict.get("dm"):
                            for raven_users in raven_notification_dict.get("dm"):
                                
                                # channels = frappe.get_all("Raven Channel", filters={"name": channel_name}, fields=["name", "channel_name", "is_direct_message"])


                                admin_email = 'admin@example.com'
                                channel_name = f"{admin_email} _ {raven_users}"
                                 # Fetch or create a direct message channel
                                channel_id = frappe.db.get_value('Raven Channel', 
                                    {
                                        "channel_name": channel_name,
                                        "is_direct_message": 1
                                    }, 
                                    'name'
                                )
                                # Create a new Raven Channel for direct messages
                                if not channel_id:
                                    channel_doc = frappe.new_doc('Raven Channel')
                                    channel_doc.channel_name = channel_name
                                    channel_doc.is_direct_message = True
                                    channel_doc.is_self_message = False  # Admin is not messaging themselves
                                    channel_doc.save()
                                    frappe.db.commit()
                                    channel_id = channel_doc.name
                                    print(f"Created new Raven Channel with ID: {channel_id}")
                                else:
                                    print(f"Fetched existing Raven Channel with ID: {channel_id}")
                                
                                # Create and send Raven Message
                                if channel_id:
                                    
                                    selected_channel = channel_id
                                    raven_message = raven_channel[0].get("message")
                                    rendered_message = render_message_template(raven_message, doc)
                                    if raven_channel[0].get("json"):
                                        json_data = get_data_from_json(doc,raven_channel[0].get("json"))
                                    else:
                                        json_data = '{}'
                                    link = raven_channel[0].get("link")
                                    if raven_notification_dict.get("subject"):
                                        subject =  raven_notification_dict.get("subject")
                                    else:
                                        subject = ''
                                    # this is for pdf generation
                                    # pdf_link = raven_channel[0].get("pdf_link")

                                    # get_pdf(doc.doctype, doc.name, raven_channel[0].get("print_format"), doc=None, no_letterhead=0, language=None, letterhead=None)
                                    # pdf_url = generate_pdf_from_doc("Sales Invoice", "ACC-SINV-2024-00003", raven_channel[0].get("print_format"), doc=doc)

                                    # pdf_url = generate_pdf_from_doc(doc, print_format=raven_channel[0].get("print_format"),no_letterhead=0)


                                    create_and_send_raven_message(doc, subject,selected_channel, rendered_message,json_data,link,need_approval_button)
                                    print(f"Created new Raven Message linked to Channel ID: {channel_id}")
                                else:
                                    print(f"Cannot create Raven Message; no valid Channel ID found.")        
                            


        else:
            pass 
            
    except Exception as e:
        frappe.msgprint(f"An error occurred: {e}")





# here is code for fetch raven channels
def get_raven_channel(doctype, method):
    # Map the method/event to the corresponding event name used in Raven Notification
    event_map = {
        "validate": "Save",
        "on_submit": "Submit",
        "on_cancel": "Cancel",
        "after_insert":"New"
    }

   
     # Check if the method is mapped to a valid event
    if method in event_map:
        event = event_map[method]
        # Fetch Raven notifications based on the document type, event, and enabled status
        raven_notification = frappe.db.get_all(
            "Raven Notification",
            filters={"document_type": doctype, "event": event, "enabled": 1},
            fields=["subject" ,"channel","name","condition", "message", "json", "link", "pdf_link", "print_format","need_approval_button"],
            ignore_permissions=True
        )
        # Process each notification to fetch channels
        if raven_notification:
            for raven_notification_row in raven_notification:
               
                # Check if the channel type is 'Channel' and fetch the relevant Raven channels
                if raven_notification_row.get("channel") == 'Channel':
                    
                    
                    raven_notification_doc = frappe.get_doc("Raven Notification", raven_notification_row.get("name")).as_dict()
                   
                    raven_channels = [channel.get('raven_channel') for channel in raven_notification_doc.raven_channel]
                  
                    raven_notification_row.update({'raven_channel' :raven_channels})                
                else:
                    # Fetch direct message users if the channel type is 'dm'
                    raven_notification_doc = frappe.get_doc("Raven Notification", raven_notification_row.get("name")).as_dict()
                   
                    raven_channels = [channel.get('raven_users') for channel in raven_notification_doc.dm]
                   
                    raven_notification_row.update({'dm' : raven_channels})   
                    



        return raven_notification




    return None



# ==== this code is for daily event of raven notification===
# this function is calling in hooks for send msg to raven for daily
def send_raven_for_daily():
    # Call the function to get Raven notifications for daily events
    get_raven_notification_for_daily(None, 'daily')


    
    return

def get_raven_notification_for_daily(doctype, method=None):
    from frappe.email.doctype.notification.notification import get_documents_for_today
    import frappe
    
    if method == 'daily':
        # Fetch all active Raven notifications with events "Days Before" or "Days After"
        raven_notification = frappe.db.get_list(
            "Raven Notification",
            filters={ "event":("in", ("Days Before", "Days After")), "enabled": 1},
            fields=["raven_channel","subject" ,"channel","name","condition", 'date_changed','days_in_advance',"message", "json", "link", "pdf_link", "print_format"],
            # ignore_permissions= True
        )
        
        
        if raven_notification:
            # Get the document object for each Raven Notification row
            for raven_notification_row in raven_notification:
                
                raven_notification_doc = frappe.get_doc("Raven Notification", raven_notification_row.get("name"))
                
                # If there is a callable function to get documents for today
                if callable(get_documents_for_today):
                    documents_for_today = raven_notification_doc.get_documents_for_today()
                    for doc in documents_for_today:
                       
                
                        # Determine the channels based on the notification row configuration
                        if raven_notification_row.get("channel") == 'Channel':
                            # Get all Raven channels linked to the notification
                            raven_channels = [channel.get('raven_channel') for channel in raven_notification_doc.raven_channel]
                            raven_notification_row.update({'raven_channel': raven_channels})
                            
                        else:
                            # Get all direct messages linked to the notification
                            raven_channels = [channel.get('raven_users') for channel in raven_notification_doc.dm]
                            raven_notification_row.update({'dm': raven_channels})
                           
                        # Retrieve the notification channel
                        raven_channel = raven_notification

                        if raven_channel:
                            # Iterate through each notification dictionary
                            for raven_notification_dict in raven_channel:
                                
                                condition = raven_notification_dict.get("condition")
                                need_approval_button = raven_notification_dict.get("need_approval_button")
                                if condition:
                                    
                                    if eval(condition):
                                        # Process if the condition is met
                                        if raven_notification_dict.get("raven_channel"):
                                            for channel_name in raven_notification_dict.get("raven_channel"):
                                                channels = frappe.get_all("Raven Channel", filters={"name": channel_name}, fields=["name", "channel_name", "is_direct_message"])
                                                # If the channel is found and not a direct message, send a message to the channel
                                                if channels and channels[0].get("is_direct_message") == 0:
                                                    selected_channel = channels[0].get("name")
                                                    raven_message = raven_channel[0].get("message")
                                                    rendered_message = render_message_template(raven_message, doc)
                                                    if raven_channel[0].get("json"):
                                                        json_data = get_data_from_json(doc,raven_channel[0].get("json"))
                                                    else:
                                                        json_data = '{}'
                                                    link = raven_channel[0].get("link")

                                                    if raven_notification_dict.get("subject"):
                                                        subject =  raven_notification_dict.get("subject")
                                                    else:
                                                        subject = ''
                                                    # this is for pdf generation
                                                    # pdf_link = raven_channel[0].get("pdf_link")

                                                    # get_pdf(doc.doctype, doc.name, raven_channel[0].get("print_format"), doc=None, no_letterhead=0, language=None, letterhead=None)
                                                    # pdf_url = generate_pdf_from_doc("Sales Invoice", "ACC-SINV-2024-00003", raven_channel[0].get("print_format"), doc=doc)

                                                    # pdf_url = generate_pdf_from_doc(doc, print_format=raven_channel[0].get("print_format"),no_letterhead=0)


                                                    create_and_send_raven_message(doc,subject ,selected_channel, rendered_message,json_data,link,need_approval_button)
                                                else:
                                                    frappe.msgprint("No channels found")
                                        else:
                                            # Process direct messages if channel is not specified
                                            if raven_notification_dict.get("dm"):
                                                for raven_users in raven_notification_dict.get("dm"):
                                                    
                                                    # channels = frappe.get_all("Raven Channel", filters={"name": channel_name}, fields=["name", "channel_name", "is_direct_message"])


                                                    admin_email = 'admin@example.com'
                                                    channel_name = f"{admin_email} _ {raven_users}"
                                                    channel_id = frappe.db.get_value('Raven Channel', 
                                                        {
                                                            "channel_name": channel_name,
                                                            "is_direct_message": 1
                                                        }, 
                                                        'name'
                                                    )
                                                    # Create a new channel if it does not exist
                                                    if not channel_id:
                                                        channel_doc = frappe.new_doc('Raven Channel')
                                                        channel_doc.channel_name = channel_name
                                                        channel_doc.is_direct_message = True
                                                        channel_doc.is_self_message = False  # Admin is not messaging themselves
                                                        channel_doc.save()
                                                        frappe.db.commit()
                                                        channel_id = channel_doc.name
                                                        print(f"Created new Raven Channel with ID: {channel_id}")
                                                    else:
                                                        print(f"Fetched existing Raven Channel with ID: {channel_id}")
                                                    
                                                    # Create and send Raven Message
                                                    if channel_id:
                                                        
                                                        selected_channel = channel_id
                                                        raven_message = raven_channel[0].get("message")
                                                        rendered_message = render_message_template(raven_message, doc)
                                                        if raven_channel[0].get("json"):
                                                            json_data = get_data_from_json(doc,raven_channel[0].get("json"))
                                                        else:
                                                            json_data = '{}'
                                                        link = raven_channel[0].get("link")

                                                        if raven_notification_dict.get("subject"):
                                                            subject =  raven_notification_dict.get("subject")
                                                        else:
                                                            subject = ''
                                                        # this is for pdf generation
                                                        # pdf_link = raven_channel[0].get("pdf_link")

                                                        # get_pdf(doc.doctype, doc.name, raven_channel[0].get("print_format"), doc=None, no_letterhead=0, language=None, letterhead=None)
                                                        # pdf_url = generate_pdf_from_doc("Sales Invoice", "ACC-SINV-2024-00003", raven_channel[0].get("print_format"), doc=doc)

                                                        # pdf_url = generate_pdf_from_doc(doc, print_format=raven_channel[0].get("print_format"),no_letterhead=0)


                                                        create_and_send_raven_message(doc, subject,selected_channel, rendered_message,json_data,link,need_approval_button)
                                                        print(f"Created new Raven Message linked to Channel ID: {channel_id}")
                                                    else:
                                                        print(f"Cannot create Raven Message; no valid Channel ID found.")
                                else:
                                    # Process direct messages if channel is not specified
                                    if raven_notification_dict.get("raven_channel"):
                                        # print(raven_notification_dict.get("raven_channel"),"====raven_notification_dict.get======")
                                        for channel_name in raven_notification_dict.get("raven_channel"):
                                            channels = frappe.get_all("Raven Channel", filters={"name": channel_name}, fields=["name", "channel_name", "is_direct_message"])
                                            
                                            # frappe.msgprint(f"{channels},===========")
                                            if channels and channels[0].get("is_direct_message") == 0:
                                                selected_channel = channels[0].get("name")
                                                raven_message = raven_channel[0].get("message")
                                                rendered_message = render_message_template(raven_message, doc)
                                                if raven_channel[0].get("json"):
                                                    json_data = get_data_from_json(doc,raven_channel[0].get("json"))
                                                else:
                                                    json_data = '{}'
                                                link = raven_channel[0].get("link")
                                                if raven_notification_dict.get("subject"):
                                                    subject =  raven_notification_dict.get("subject")
                                                else:
                                                    subject = ''
                                                # this is for pdf generation
                                                # pdf_link = raven_channel[0].get("pdf_link")

                                                # get_pdf(doc.doctype, doc.name, raven_channel[0].get("print_format"), doc=None, no_letterhead=0, language=None, letterhead=None)
                                                # pdf_url = generate_pdf_from_doc("Sales Invoice", "ACC-SINV-2024-00003", raven_channel[0].get("print_format"), doc=doc)

                                                # pdf_url = generate_pdf_from_doc(doc, print_format=raven_channel[0].get("print_format"),no_letterhead=0)


                                                create_and_send_raven_message(doc, subject,selected_channel, rendered_message,json_data,link,need_approval_button)
                                            else:
                                                frappe.msgprint("No channels found")
                                    else:
                                        if raven_notification_dict.get("dm"):
                                            for raven_users in raven_notification_dict.get("dm"):
                                                
                                                # frappe.msgprint(f"{raven_users},===========raven_users")
                                                # channels = frappe.get_all("Raven Channel", filters={"name": channel_name}, fields=["name", "channel_name", "is_direct_message"])


                                                admin_email = 'admin@example.com'
                                                channel_name = f"{admin_email} _ {raven_users}"
                                                channel_id = frappe.db.get_value('Raven Channel', 
                                                    {
                                                        "channel_name": channel_name,
                                                        "is_direct_message": 1
                                                    }, 
                                                    'name'
                                                )
                                                # Create a new channel if it does not exist
                                                if not channel_id:
                                                    channel_doc = frappe.new_doc('Raven Channel')
                                                    channel_doc.channel_name = channel_name
                                                    channel_doc.is_direct_message = True
                                                    channel_doc.is_self_message = False  # Admin is not messaging themselves
                                                    channel_doc.save()
                                                    frappe.db.commit()
                                                    channel_id = channel_doc.name
                                                    print(f"Created new Raven Channel with ID: {channel_id}")
                                                else:
                                                    print(f"Fetched existing Raven Channel with ID: {channel_id}")
                                                
                                                # Create and send Raven Message
                                                if channel_id:
                                                    
                                                    # frappe.msgprint(f"{channel_id}=========channel_idchannel_id")
                                                    selected_channel = channel_id
                                                    raven_message = raven_channel[0].get("message")
                                                    rendered_message = render_message_template(raven_message, doc)
                                                    if raven_channel[0].get("json"):
                                                        json_data = get_data_from_json(doc,raven_channel[0].get("json"))
                                                    else:
                                                        json_data = '{}'
                                                    link = raven_channel[0].get("link")
                                                    if raven_notification_dict.get("subject"):
                                                        subject =  raven_notification_dict.get("subject")
                                                    else:
                                                        subject = ''
                                                    # this is for pdf generation
                                                    # pdf_link = raven_channel[0].get("pdf_link")

                                                    # get_pdf(doc.doctype, doc.name, raven_channel[0].get("print_format"), doc=None, no_letterhead=0, language=None, letterhead=None)
                                                    # pdf_url = generate_pdf_from_doc("Sales Invoice", "ACC-SINV-2024-00003", raven_channel[0].get("print_format"), doc=doc)

                                                    # pdf_url = generate_pdf_from_doc(doc, print_format=raven_channel[0].get("print_format"),no_letterhead=0)


                                                    create_and_send_raven_message(doc, subject,selected_channel, rendered_message,json_data,link,need_approval_button)
                                                    print(f"Created new Raven Message linked to Channel ID: {channel_id}")
                                                else:
                                                    print(f"Cannot create Raven Message; no valid Channel ID found.")        
                                            


                        else:
                            pass 

                        
    
# Utility function to create a context for rendering
def get_context(doc):
    Frappe = namedtuple("frappe", ["utils"])
    return {
        "doc": doc,
        "nowdate": nowdate,
        "frappe": Frappe(utils=get_safe_globals().get("frappe").get("utils")),
    }

# get list of documents that will be triggered today
# Class definition for RavenNotification
class RavenNotification(Document):
    # Method to get documents that will be triggered today
    def get_documents_for_today(self):
            """get list of documents that will be triggered today"""
            docs = []
            # Calculate the reference date based on the event and days in advance
            diff_days = self.days_in_advance
            if self.event == "Days After":
                diff_days = -diff_days

            # Determine the start and end of the reference date
            reference_date = add_to_date(nowdate(), days=diff_days)
            reference_date_start = reference_date + " 00:00:00.000000"
            reference_date_end = reference_date + " 23:59:59.000000"
            # Fetch documents within the reference date range
            doc_list = frappe.get_all(
                self.document_type,
                fields="name",
                filters=[
                    {self.date_changed: (">=", reference_date_start)},
                    {self.date_changed: ("<=", reference_date_end)},
                ],
            )
            # Filter documents based on condition if provided
            for d in doc_list:
                doc = frappe.get_doc(self.document_type, d.name)

                if self.condition and not frappe.safe_eval(self.condition, None, get_context(doc)):
                    continue

                docs.append(doc)

            return docs



# This code for value change event of raven notification
# Trigger function for value change event
def trigger_on_save_for_value_change(doc, method):
    # Fetch Raven notifications that are enabled and have 'Value Change' event
    raven_notification = frappe.db.get_all(
            "Raven Notification",
            filters={"document_type": doc.doctype, "event": 'Value Change', "enabled": 1},
            fields=["subject" ,"channel","event","value_changed","name","condition", "message", "json", "link", "pdf_link", "print_format","need_approval_button"],
            ignore_permissions=True
        )

    if raven_notification:
        for raven_notification_row in raven_notification:
            
            # Update raven_notification_row with channels based on its type
            if raven_notification_row.get("channel") == 'Channel':
                
                
                raven_notification_doc = frappe.get_doc("Raven Notification", raven_notification_row.get("name")).as_dict()
                
                raven_channels = [channel.get('raven_channel') for channel in raven_notification_doc.raven_channel]
                

                
                raven_notification_row.update({'raven_channel' :raven_channels})                
            else:
                raven_notification_doc = frappe.get_doc("Raven Notification", raven_notification_row.get("name")).as_dict()
                
                raven_channels = [channel.get('raven_users') for channel in raven_notification_doc.dm]
                
                raven_notification_row.update({'dm' : raven_channels})   

            
                


    
    # Check for value changes and process notifications accordingly
    if raven_notification:
        for row in raven_notification:
            value_changed = row.get("value_changed")
            if value_changed:
                old_doc = frappe.db.get_all(doctype=doc.doctype,filters={"name": doc.name},fields=["name", value_changed])
                if old_doc and old_doc[0].get(value_changed):
                    if old_doc[0].get(value_changed) != doc.get(value_changed):

                        raven_channel = raven_notification

                        if raven_channel:
                            
                            for raven_notification_dict in raven_channel:
                                
                                condition = raven_notification_dict.get("condition")
                                need_approval_button = raven_notification_dict.get("need_approval_button")
                                if condition:
                                    
                                    if eval(condition):
                                        if raven_notification_dict.get("raven_channel"):
                                            for channel_name in raven_notification_dict.get("raven_channel"):
                                                channels = frappe.get_all("Raven Channel", filters={"name": channel_name}, fields=["name", "channel_name", "is_direct_message"])
                                                
                                                if channels and channels[0].get("is_direct_message") == 0:
                                                    selected_channel = channels[0].get("name")
                                                    raven_message = raven_channel[0].get("message")
                                                    rendered_message = render_message_template(raven_message, doc)
                                                    if raven_channel[0].get("json"):
                                                        json_data = get_data_from_json(doc,raven_channel[0].get("json"))
                                                    else:
                                                        json_data = '{}'
                                                    link = raven_channel[0].get("link")

                                                    if raven_notification_dict.get("subject"):
                                                        subject =  raven_notification_dict.get("subject")
                                                    else:
                                                        subject = ''
                                                    # this is for pdf generation
                                                    # pdf_link = raven_channel[0].get("pdf_link")

                                                    # get_pdf(doc.doctype, doc.name, raven_channel[0].get("print_format"), doc=None, no_letterhead=0, language=None, letterhead=None)
                                                    # pdf_url = generate_pdf_from_doc("Sales Invoice", "ACC-SINV-2024-00003", raven_channel[0].get("print_format"), doc=doc)

                                                    # pdf_url = generate_pdf_from_doc(doc, print_format=raven_channel[0].get("print_format"),no_letterhead=0)


                                                    create_and_send_raven_message(doc,subject ,selected_channel, rendered_message,json_data,link,need_approval_button)
                                                else:
                                                    frappe.msgprint("No channels found")
                                        else:
                                            if raven_notification_dict.get("dm"):
                                                for raven_users in raven_notification_dict.get("dm"):
                                                    # frappe.msgprint(f"{raven_users},===========raven_users")
                                                    # channels = frappe.get_all("Raven Channel", filters={"name": channel_name}, fields=["name", "channel_name", "is_direct_message"])


                                                    admin_email = 'admin@example.com'
                                                    channel_name = f"{admin_email} _ {raven_users}"
                                                    channel_id = frappe.db.get_value('Raven Channel', 
                                                        {
                                                            "channel_name": channel_name,
                                                            "is_direct_message": 1
                                                        }, 
                                                        'name'
                                                    )
                                                    
                                                    if not channel_id:
                                                        channel_doc = frappe.new_doc('Raven Channel')
                                                        channel_doc.channel_name = channel_name
                                                        channel_doc.is_direct_message = True
                                                        channel_doc.is_self_message = False  # Admin is not messaging themselves
                                                        channel_doc.save()
                                                        frappe.db.commit()
                                                        channel_id = channel_doc.name
                                                        print(f"Created new Raven Channel with ID: {channel_id}")
                                                    else:
                                                        print(f"Fetched existing Raven Channel with ID: {channel_id}")
                                                    
                                                    # Create and send Raven Message
                                                    if channel_id:
                                                        
                                                        selected_channel = channel_id
                                                        raven_message = raven_channel[0].get("message")
                                                        rendered_message = render_message_template(raven_message, doc)
                                                        if raven_channel[0].get("json"):
                                                            json_data = get_data_from_json(doc,raven_channel[0].get("json"))
                                                        else:
                                                            json_data = '{}'
                                                        link = raven_channel[0].get("link")

                                                        if raven_notification_dict.get("subject"):
                                                            subject =  raven_notification_dict.get("subject")
                                                        else:
                                                            subject = ''
                                                        # this is for pdf generation
                                                        # pdf_link = raven_channel[0].get("pdf_link")

                                                        # get_pdf(doc.doctype, doc.name, raven_channel[0].get("print_format"), doc=None, no_letterhead=0, language=None, letterhead=None)
                                                        # pdf_url = generate_pdf_from_doc("Sales Invoice", "ACC-SINV-2024-00003", raven_channel[0].get("print_format"), doc=doc)

                                                        # pdf_url = generate_pdf_from_doc(doc, print_format=raven_channel[0].get("print_format"),no_letterhead=0)


                                                        create_and_send_raven_message(doc, subject,selected_channel, rendered_message,json_data,link,need_approval_button)
                                                        print(f"Created new Raven Message linked to Channel ID: {channel_id}")
                                                    else:
                                                        print(f"Cannot create Raven Message; no valid Channel ID found.")
                                else:
                                    
                                    if raven_notification_dict.get("raven_channel"):
                                        
                                        for channel_name in raven_notification_dict.get("raven_channel"):
                                            channels = frappe.get_all("Raven Channel", filters={"name": channel_name}, fields=["name", "channel_name", "is_direct_message"])
                                            
                                            
                                            if channels and channels[0].get("is_direct_message") == 0:
                                                selected_channel = channels[0].get("name")
                                                raven_message = raven_channel[0].get("message")
                                                rendered_message = render_message_template(raven_message, doc)
                                                if raven_channel[0].get("json"):
                                                    json_data = get_data_from_json(doc,raven_channel[0].get("json"))
                                                else:
                                                    json_data = '{}'
                                                link = raven_channel[0].get("link")
                                                if raven_notification_dict.get("subject"):
                                                    subject =  raven_notification_dict.get("subject")
                                                else:
                                                    subject = ''
                                                # this is for pdf generation
                                                # pdf_link = raven_channel[0].get("pdf_link")

                                                # get_pdf(doc.doctype, doc.name, raven_channel[0].get("print_format"), doc=None, no_letterhead=0, language=None, letterhead=None)
                                                # pdf_url = generate_pdf_from_doc("Sales Invoice", "ACC-SINV-2024-00003", raven_channel[0].get("print_format"), doc=doc)

                                                # pdf_url = generate_pdf_from_doc(doc, print_format=raven_channel[0].get("print_format"),no_letterhead=0)


                                                create_and_send_raven_message(doc, subject,selected_channel, rendered_message,json_data,link,need_approval_button)
                                            else:
                                                frappe.msgprint("No channels found")
                                    else:
                                        if raven_notification_dict.get("dm"):
                                            for raven_users in raven_notification_dict.get("dm"):
            


                                                admin_email = 'admin@example.com'
                                                channel_name = f"{admin_email} _ {raven_users}"
                                                channel_id = frappe.db.get_value('Raven Channel', 
                                                    {
                                                        "channel_name": channel_name,
                                                        "is_direct_message": 1
                                                    }, 
                                                    'name'
                                                )
                                                
                                                if not channel_id:
                                                    channel_doc = frappe.new_doc('Raven Channel')
                                                    channel_doc.channel_name = channel_name
                                                    channel_doc.is_direct_message = True
                                                    channel_doc.is_self_message = False  # Admin is not messaging themselves
                                                    channel_doc.save()
                                                    frappe.db.commit()
                                                    channel_id = channel_doc.name
                                                    print(f"Created new Raven Channel with ID: {channel_id}")
                                                else:
                                                    print(f"Fetched existing Raven Channel with ID: {channel_id}")
                                                
                                                # Create and send Raven Message
                                                if channel_id:
                                                    
                                                    
                                                    selected_channel = channel_id
                                                    raven_message = raven_channel[0].get("message")
                                                    rendered_message = render_message_template(raven_message, doc)
                                                    if raven_channel[0].get("json"):
                                                        json_data = get_data_from_json(doc,raven_channel[0].get("json"))
                                                    else:
                                                        json_data = '{}'
                                                    link = raven_channel[0].get("link")
                                                    if raven_notification_dict.get("subject"):
                                                        subject =  raven_notification_dict.get("subject")
                                                    else:
                                                        subject = ''
                                                    # this is for pdf generation
                                                    # pdf_link = raven_channel[0].get("pdf_link")

                                                    # get_pdf(doc.doctype, doc.name, raven_channel[0].get("print_format"), doc=None, no_letterhead=0, language=None, letterhead=None)
                                                    # pdf_url = generate_pdf_from_doc("Sales Invoice", "ACC-SINV-2024-00003", raven_channel[0].get("print_format"), doc=doc)

                                                    # pdf_url = generate_pdf_from_doc(doc, print_format=raven_channel[0].get("print_format"),no_letterhead=0)


                                                    create_and_send_raven_message(doc, subject,selected_channel, rendered_message,json_data,link,need_approval_button)
                                                    print(f"Created new Raven Message linked to Channel ID: {channel_id}")
                                                else:
                                                    print(f"Cannot create Raven Message; no valid Channel ID found.")        
                                            
                        else:
                            pass 

                        
    
    return raven_notification


    
# this code fetching data from json data
def get_data_from_json(doc, json_data_str):
    import json
    from datetime import date
    # Parse the JSON string to a Python dictionary
    json_data = json.loads(json_data_str)
    extracted_data = {}

    # Extract fields from the main document (doctype fields)
    doctype_fields = json_data.get("doctype_fields", {})
    for field in doctype_fields:
        value = doc.get(field)
        if isinstance(value, date):
            value = value.isoformat()  
        extracted_data[field] = value

   # Extract fields from the child tables
    child_table_fields = json_data.get("child_table_fields", {})
    for child_table, fields in child_table_fields.items():
        # Get the child table entries from the document
        child_entries = doc.get(child_table, [])
        
        # Initialize a list to store extracted data for each child table
        extracted_data[child_table] = []

       # Iterate over each entry in the child table and extract specified fields
        for entry in child_entries:
            row_data = {}
            for field in fields:
                value = entry.get(field)
                # Convert date fields to ISO format string
                if isinstance(value, date):
                    value = value.isoformat()  
                row_data[field] = value
            extracted_data[child_table].append(row_data)

    return extracted_data


# Create a Template object from the provided template string and render it using the given 'doc' dictionary.
# this code is creating message template for raven from raven notification
def render_message_template(template_str, doc):
    template = Template(template_str)
    return template.render(doc=doc)


import json
from markupsafe import Markup

def json_to_html(json_data):
    """
    Converts JSON data to an HTML representation. This function expects JSON data to be in a dictionary format 
    with possible child table entries represented as lists.

    Args:
        json_data (str or dict): The JSON data to convert. Can be a JSON string or a dictionary.

    Returns:
        Markup: An HTML representation of the JSON data.
    """
    # Check if json_data is a string and try to parse it
    if isinstance(json_data, str):
        try:
            json_data = json.loads(json_data)
        except json.JSONDecodeError as e:
            return f"Error decoding JSON: {str(e)}"

    html_content = ""

    # Check if json_data is a dictionary
    if isinstance(json_data, dict):
        main_fields = {} # To store main fields
        child_table_fields = {}   # To store fields for child tables

        # Separate main fields and child table fields
        for key, value in json_data.items():
            if isinstance(value, list): 
                child_table_fields[key] = value
            else:
                main_fields[key] = value

        # Generate HTML for main fields
        for key, value in main_fields.items():
            html_content += f"<p><strong>{key}:</strong> {value}</p>"

        # Generate HTML for child table fields
        for table_name, rows in child_table_fields.items():
            if rows: # Only process non-empty child table fields
                headers = rows[0].keys() # Get the headers for the table

                # Create table HTML
                html_content += f"<p><strong>{table_name}:</strong></p>"
                html_content += "<table border='1' style='border-collapse: collapse; width: 100%;'>"
                html_content += "<tr>"
                for header in headers:
                    html_content += f"<th>{header}</th>"
                html_content += "</tr>"

                # Fill table rows with data
                for row in rows:
                    html_content += "<tr>"
                    for header in headers:
                        cell_value = row.get(header, "")
                        html_content += f"<td>{cell_value if cell_value is not None else ''}</td>"
                    html_content += "</tr>"

                html_content += "</table>"
    else:
        return "Invalid JSON data format. Expected a dictionary."

    return Markup(html_content)


# ==== Below code is only for change workflow state through raven
# ================================================================
import frappe
from datetime import date
from frappe.utils.background_jobs import enqueue
from frappe.workflow.doctype.workflow_action.workflow_action import get_next_possible_transitions,get_doc_workflow_state
from frappe.model.workflow import get_workflow_name,apply_workflow
from frappe.utils.verified_command import get_signed_params, verify_request
from frappe.utils import get_url, get_datetime
# from hkm.erpnext___custom.doc_workflow.je.mail_templates import journal_entry_mail
import socket


# Function to check if a user is eligible to change the workflow state
def check_user_eligible(user,transition,doc):
    
    roles = frappe.get_roles(user)
    # Checks if the user has the role allowed for the transition and if any conditions are met
    if transition['allowed'] in roles and ((transition['condition'] is None) or eval(transition['condition'].replace('frappe.session.user','user'))):
        return True
    return False

# Get the allowed workflow actions for a user on a specific document
def get_allowed_options(user,doc):
    
    workflow = get_workflow_name(doc.get('doctype'))
    # Retrieve transitions from the Workflow Transition doctype that are applicable to the document's current state
    transitions = frappe.get_all('Workflow Transition', fields=['allowed', 'action', 'state', 'allow_self_approval', 'next_state', '`condition`'], filters=[['parent', '=', workflow],['state', '=', get_doc_workflow_state(doc)]])
    applicable_actions = []
    # Check which transitions the user is eligible for
    for transition in transitions:
        if check_user_eligible(user,transition,doc):
            applicable_actions.append(transition['action'])
     # Remove duplicate actions
    applicable_actions_unique = set(applicable_actions)
    frappe.errprint(applicable_actions_unique)
    return applicable_actions_unique


# Generate HTML for assigning workflow actions to a user
def assign(user,doc):
    allowed_options = get_allowed_options(user,doc)
    
    # Construct the HTML string with buttons for each allowed workflow action
    option_string = ""
    for option in allowed_options:
        # if option not in ['Trash']:
        url = get_confirm_workflow_action_url(doc, option, user)
        
        option_string= option_string +"""
                <p>
                <a 
                style="	background-color: #ffe70a;
                        border: none; 
                        color: black; 
                        padding: 15px 32px; 
                        text-align: center; 
                        text-decoration: none; 
                        display: inline-block; 
                        font-size: 16px;" 
                        href="{}">{}</a></p>
                </p>
                """.format(get_confirm_workflow_action_url(doc, option, user),option)
    return option_string
            
# Generate URL for applying a workflow action
def get_workflow_action_url(action, doc, user):
	apply_action_method = "/api/method/hkm.erpnext___custom.doc_workflow.je.notification.apply_action"

	params = {
		"doctype": doc.get('doctype'),
		"docname": doc.get('name'),
		"action": action,
		"current_state": get_doc_workflow_state(doc),
		"user": user,
		"last_modified": doc.get('modified')
	}
	frappe.log_error(f'act,{action}')

	return get_url(apply_action_method + "?" + get_signed_params(params))
            

# Generate URL for confirming a workflow action via Raven notification
def get_confirm_workflow_action_url(doc, action, user):


    raven_notification = frappe.db.get_all(
            "Raven Notification",
            filters={"document_type": doc.doctype, "enabled": 1},
            fields=["subject" ,"channel","name","condition", "message", "json", "link", "pdf_link", "print_format","need_approval_button"],
            ignore_permissions=True
        )
    
    # response = requests.post(get_site_url(frappe.local.site) + "/api/method/test_server_script")

    confirm_action_method = "/api/method/mdpl.mdpl.doctype.raven_notification.raven_notification.confirm_action"
    # Parameters required for signing the request URL
    params = {
		"action": action,
		"doctype": doc.get('doctype'),
		"docname": doc.get('name'),
		"user": user
	}
    # frappe.log_error(f'act1,{action}')

   
    host = raven_notification[0].get("pdf_link")
    
    return 'http://'+host + confirm_action_method + '?' + get_signed_params(params)
    # return get_url(confirm_action_method + "?" + get_signed_params(params))


# Endpoint to confirm a workflow action (exposed to the public)
@frappe.whitelist(allow_guest=True)
def confirm_action(doctype, docname, user, action):
    if not verify_request():
        return

    logged_in_user = frappe.session.user
    if logged_in_user == 'Guest' and user:
		# to allow user to apply action without login
        frappe.set_user(user)
    doc = frappe.get_doc(doctype, docname)

	### Additional by NRHD
    # workflow_state = get_doc_workflow_state(doc)
	
    # return_already_approved_page(doc)
	###
	
    if action:
        newdoc = apply_workflow(doc, action)
        frappe.db.commit()
        return_success_page(newdoc)

	# reset session user
    if logged_in_user == 'Guest':
        frappe.set_user(logged_in_user)

# Return a success page indicating that the workflow action was successful  
def return_success_page(doc):
	frappe.respond_as_web_page(("Success"),
		("{0}: {1} is set to state {2}").format(
			doc.get('doctype'),
			frappe.bold(doc.get('name')),
			frappe.bold(get_doc_workflow_state(doc))
		), indicator_color='green')

# return already approved page 
# Return a page indicating the document has already been approved
def return_already_approved_page(doc):
	frappe.respond_as_web_page(("Already Approved"),
		("The doument ( {0} ) is already {1}.").format(
			frappe.bold(doc.get('name')),
			frappe.bold(get_doc_workflow_state(doc))
		), indicator_color='yellow')
# ======================================================================================


from frappe import _

import frappe
import json
from markupsafe import Markup

# this function is prepare for send raven message
# def create_and_send_raven_message(doc, subject,channel, raven_message, json_data, link):
#     # fetch session user
#     user = frappe.session.user
#     # Generate HTML for assigning workflow actions to a user
#     action = assign(user,doc)
    
#     try:
        
#         if isinstance(json_data, dict):
#             json_data_str = json.dumps(json_data)
#         else:
#             json_data_str = json_data
        
#         json_html = json_to_html(json_data_str)
#         # prepare subject for raven message
#         subject = frappe.render_template(subject, {'doc': doc})

#         html = "<p><a style='	background-color: #ffe70a;border: none; color: black; padding: 15px 32px; text-align: center; text-decoration: none; display: inline-block; font-size: 16px;' href='Reject'>Approved</a></p></p>"
#         # this is the action button for workflow
#         button = frappe.render_template(action,{'doc':doc})
        
#         rendered_message = Markup(
#             # f"<b>{subject}</b><br>"
#             f"<h2><b>{subject}</b></h2><br>"
#             f"{raven_message}<br>{json_html}<br>"
#             f"<a href='{link}{doc.name}'> Go To {doc.doctype} {doc.name}</a><br>"
#             # f"<a href='{link}{doc.name}' onclick='update_status(\"{doc.name}\", \"{doc.doctype}\");'><button type='button'>Preview</button></a>"
#             f"{button}"
#         ) 
#         # create new doc for raven message 
#         raven_message_doc = frappe.new_doc("Raven Message")
#         raven_message_doc.text = rendered_message
#         raven_message_doc.channel_id = channel
#         raven_message_doc.json = json_data
#         raven_message_doc.save()
        
#         frappe.db.commit()
#         process_message(doc, channel, raven_message)
#     except Exception as e:
#         frappe.msgprint(f"An error occurred while creating or sending the Raven message: {e}")

def create_and_send_raven_message(doc, subject, channel, raven_message, json_data, link, need_approval_button):
    # fetch session user
    user = frappe.session.user
    # Generate HTML for assigning workflow actions to a user
    action = assign(user, doc)
    
    try:
        # Convert json_data to string if it is a dict
        if isinstance(json_data, dict):
            json_data_str = json.dumps(json_data)
        else:
            json_data_str = json_data
        
        # Convert JSON to HTML
        json_html = json_to_html(json_data_str)
        
        # Prepare subject for raven message
        subject = frappe.render_template(subject, {'doc': doc})

        # Initialize rendered message content
        rendered_message = Markup(
            f"<h2><b>{subject}</b></h2><br>"
            f"{raven_message}<br>{json_html}<br>"
            f"<a href='{link}{doc.name}'> Go To {doc.doctype} {doc.name}</a><br>"
        )

        # Conditionally add the approval button if needed
        if need_approval_button == 1:
            button = frappe.render_template(action, {'doc': doc})
            rendered_message += Markup(f"{button}")

        # Create a new Raven Message document
        raven_message_doc = frappe.new_doc("Raven Message")
        raven_message_doc.text = rendered_message
        raven_message_doc.channel_id = channel
        raven_message_doc.json = json_data
        raven_message_doc.save()
        
        # Commit to the database
        frappe.db.commit()

        # Process the message
        process_message(doc, channel, raven_message)
    
    except Exception as e:
        frappe.msgprint(f"An error occurred while creating or sending the Raven message: {e}")



        
def process_message(doc, channel, message):
    frappe.msgprint(f"<b>Sending message to channel :{channel} </b>")




# this code generating pdf 
def generate_pdf_from_doc(doc, print_format=None, no_letterhead=0):
    try:
        html = frappe.get_print(doc.doctype, doc.name, print_format=print_format, no_letterhead=no_letterhead)
        pdf_content = get_pdf(html)
        
        file_name = f"{doc.name}.pdf"
        file_path = os.path.join(frappe.get_site_path('public', 'files', file_name))

        with open(file_path, 'wb') as pdf_file:
            pdf_file.write(pdf_content)
        
        pdf_url = f"/files/{file_name}"
        frappe.msgprint(f"PDF generated and available at: {pdf_url}")

        return pdf_url

    except Exception as e:
        frappe.msgprint(f"An error occurred while generating the PDF: {e}")
        return None

        
# ================
# this method calling through hooks.py 
#  Send a Raven for Method Event 
def send_a_raven_for_method_event(doc,method):

    if method:
        # Fetch Raven Notifications based on the document type, event, method, and enabled status
        raven_notification = frappe.db.get_all(
            "Raven Notification",
            filters={"document_type": doc.doctype, "event": "Method", "method":method,"enabled": 1},
            fields=["subject" ,"channel","name","condition", "message", "json", "link", "pdf_link", "print_format","need_approval_button"],
            ignore_permissions=True
        ) 
        # If any Raven Notifications are found
        if raven_notification:
            # Iterate over each Raven Notification row
            for raven_notification_row in raven_notification:
            
                if raven_notification_row.get("channel") == 'Channel':
                    
                    # Fetch and convert Raven Notification doc into a dictionary
                    raven_notification_doc = frappe.get_doc("Raven Notification", raven_notification_row.get("name")).as_dict()
                    # Extract 'raven_channel' information
                    raven_channels = [channel.get('raven_channel') for channel in raven_notification_doc.raven_channel]
                    
                    # Update the row with fetched 'raven_channel' data
                    raven_notification_row.update({'raven_channel' :raven_channels})                
                else:
                    # Handle cases where the channel is not 'Channel' (Direct Message scenario)
                    raven_notification_doc = frappe.get_doc("Raven Notification", raven_notification_row.get("name")).as_dict()
                    # Extract 'raven_users' information for direct messages
                    raven_channels = [channel.get('raven_users') for channel in raven_notification_doc.dm]
                     # Update the row with fetched direct message channels
                    raven_notification_row.update({'dm' : raven_channels})   
                    


        # Set raven_channel to the list of fetched Raven Notifications
        raven_channel = raven_notification
        # If Raven Notifications are present
        if raven_channel:
            
            for raven_notification_dict in raven_channel:
                
                condition = raven_notification_dict.get("condition")
                need_approval_button = raven_notification_dict.get("need_approval_button")
                if condition:
                    
                    if eval(condition):
                        # If a raven channel exists, send notifications to channels
                        if raven_notification_dict.get("raven_channel"):
                            for channel_name in raven_notification_dict.get("raven_channel"):
                                # Fetch channel details from Raven Channel doctype
                                channels = frappe.get_all("Raven Channel", filters={"name": channel_name}, fields=["name", "channel_name", "is_direct_message"])
                                # If the channel is not a direct message, send notification
                                if channels and channels[0].get("is_direct_message") == 0:
                                    selected_channel = channels[0].get("name")
                                    raven_message = raven_channel[0].get("message")
                                    # Render message template and fetch JSON data
                                    rendered_message = render_message_template(raven_message, doc)
                                    if raven_channel[0].get("json"):
                                        json_data = get_data_from_json(doc,raven_channel[0].get("json"))
                                    else:
                                        json_data = '{}'
                                    link = raven_channel[0].get("link")

                                    # Get the subject for the notification
                                    if raven_notification_dict.get("subject"):
                                        subject =  raven_notification_dict.get("subject")
                                    else:
                                        subject = ''
                                    # this is for pdf generation
                                    # pdf_link = raven_channel[0].get("pdf_link")

                                    # get_pdf(doc.doctype, doc.name, raven_channel[0].get("print_format"), doc=None, no_letterhead=0, language=None, letterhead=None)
                                    # pdf_url = generate_pdf_from_doc("Sales Invoice", "ACC-SINV-2024-00003", raven_channel[0].get("print_format"), doc=doc)

                                    # pdf_url = generate_pdf_from_doc(doc, print_format=raven_channel[0].get("print_format"),no_letterhead=0)

                                    # Send the Raven Message
                                    create_and_send_raven_message(doc,subject ,selected_channel, rendered_message,json_data,link,need_approval_button)
                                else:
                                    frappe.msgprint("No channels found")
                        else:
                            # Handle sending of direct messages
                            if raven_notification_dict.get("dm"):
                                for raven_users in raven_notification_dict.get("dm"):
                                    
                                    # channels = frappe.get_all("Raven Channel", filters={"name": channel_name}, fields=["name", "channel_name", "is_direct_message"])

                                    # Prepare the direct message channel name
                                    admin_email = 'admin@example.com'
                                    channel_name = f"{admin_email} _ {raven_users}"
                                    # Check if the channel already exists
                                    channel_id = frappe.db.get_value('Raven Channel', 
                                        {
                                            "channel_name": channel_name,
                                            "is_direct_message": 1
                                        }, 
                                        'name'
                                    )
                                    # If the channel does not exist, create a new Raven Channel
                                    if not channel_id:
                                        channel_doc = frappe.new_doc('Raven Channel')
                                        channel_doc.channel_name = channel_name
                                        channel_doc.is_direct_message = True
                                        channel_doc.is_self_message = False  # Admin is not messaging themselves
                                        channel_doc.save()
                                        frappe.db.commit()
                                        channel_id = channel_doc.name
                                        print(f"Created new Raven Channel with ID: {channel_id}")
                                    else:
                                        print(f"Fetched existing Raven Channel with ID: {channel_id}")
                                    
                                    # Create and send Raven Message
                                    if channel_id:
                                        
                                        selected_channel = channel_id
                                        raven_message = raven_channel[0].get("message")
                                        rendered_message = render_message_template(raven_message, doc)
                                        if raven_channel[0].get("json"):
                                            json_data = get_data_from_json(doc,raven_channel[0].get("json"))
                                        else:
                                            json_data = '{}'
                                        link = raven_channel[0].get("link")

                                        if raven_notification_dict.get("subject"):
                                            subject =  raven_notification_dict.get("subject")
                                        else:
                                            subject = ''
                                        # this is for pdf generation
                                        # pdf_link = raven_channel[0].get("pdf_link")

                                        # get_pdf(doc.doctype, doc.name, raven_channel[0].get("print_format"), doc=None, no_letterhead=0, language=None, letterhead=None)
                                        # pdf_url = generate_pdf_from_doc("Sales Invoice", "ACC-SINV-2024-00003", raven_channel[0].get("print_format"), doc=doc)

                                        # pdf_url = generate_pdf_from_doc(doc, print_format=raven_channel[0].get("print_format"),no_letterhead=0)


                                        create_and_send_raven_message(doc, subject,selected_channel, rendered_message,json_data,link,need_approval_button)
                                        print(f"Created new Raven Message linked to Channel ID: {channel_id}")
                                    else:
                                        print(f"Cannot create Raven Message; no valid Channel ID found.")
                else:
                    # Handle cases where no condition is provided
                    if raven_notification_dict.get("raven_channel"):
                        
                        for channel_name in raven_notification_dict.get("raven_channel"):
                            channels = frappe.get_all("Raven Channel", filters={"name": channel_name}, fields=["name", "channel_name", "is_direct_message"])
                            
                           # If the channel is not a direct message, send notification
                            if channels and channels[0].get("is_direct_message") == 0:
                                selected_channel = channels[0].get("name")
                                raven_message = raven_channel[0].get("message")
                                rendered_message = render_message_template(raven_message, doc)
                                if raven_channel[0].get("json"):
                                    json_data = get_data_from_json(doc,raven_channel[0].get("json"))
                                else:
                                    json_data = '{}'
                                link = raven_channel[0].get("link")
                                if raven_notification_dict.get("subject"):
                                    subject =  raven_notification_dict.get("subject")
                                else:
                                    subject = ''
                                # this is for pdf generation
                                # pdf_link = raven_channel[0].get("pdf_link")

                                # get_pdf(doc.doctype, doc.name, raven_channel[0].get("print_format"), doc=None, no_letterhead=0, language=None, letterhead=None)
                                # pdf_url = generate_pdf_from_doc("Sales Invoice", "ACC-SINV-2024-00003", raven_channel[0].get("print_format"), doc=doc)

                                # pdf_url = generate_pdf_from_doc(doc, print_format=raven_channel[0].get("print_format"),no_letterhead=0)


                                create_and_send_raven_message(doc, subject,selected_channel, rendered_message,json_data,link,need_approval_button)
                            else:
                                frappe.msgprint("No channels found")
                    else:
                        if raven_notification_dict.get("dm"):
                            for raven_users in raven_notification_dict.get("dm"):
                               
                                
                                # channels = frappe.get_all("Raven Channel", filters={"name": channel_name}, fields=["name", "channel_name", "is_direct_message"])


                                admin_email = 'admin@example.com'
                                channel_name = f"{admin_email} _ {raven_users}"
                                channel_id = frappe.db.get_value('Raven Channel', 
                                    {
                                        "channel_name": channel_name,
                                        "is_direct_message": 1
                                    }, 
                                    'name'
                                )
                                
                                if not channel_id:
                                    channel_doc = frappe.new_doc('Raven Channel')
                                    channel_doc.channel_name = channel_name
                                    channel_doc.is_direct_message = True
                                    channel_doc.is_self_message = False  # Admin is not messaging themselves
                                    channel_doc.save()
                                    frappe.db.commit()
                                    channel_id = channel_doc.name
                                    print(f"Created new Raven Channel with ID: {channel_id}")
                                else:
                                    print(f"Fetched existing Raven Channel with ID: {channel_id}")
                                
                                # Create and send Raven Message
                                if channel_id:
                                    
                                    
                                    selected_channel = channel_id
                                    raven_message = raven_channel[0].get("message")
                                    rendered_message = render_message_template(raven_message, doc)
                                    if raven_channel[0].get("json"):
                                        json_data = get_data_from_json(doc,raven_channel[0].get("json"))
                                    else:
                                        json_data = '{}'
                                    link = raven_channel[0].get("link")
                                    if raven_notification_dict.get("subject"):
                                        subject =  raven_notification_dict.get("subject")
                                    else:
                                        subject = ''
                                    # this is for pdf generation
                                    # pdf_link = raven_channel[0].get("pdf_link")

                                    # get_pdf(doc.doctype, doc.name, raven_channel[0].get("print_format"), doc=None, no_letterhead=0, language=None, letterhead=None)
                                    # pdf_url = generate_pdf_from_doc("Sales Invoice", "ACC-SINV-2024-00003", raven_channel[0].get("print_format"), doc=doc)

                                    # pdf_url = generate_pdf_from_doc(doc, print_format=raven_channel[0].get("print_format"),no_letterhead=0)


                                    create_and_send_raven_message(doc, subject,selected_channel, rendered_message,json_data,link,need_approval_button)
                                    print(f"Created new Raven Message linked to Channel ID: {channel_id}")
                                else:
                                    print(f"Cannot create Raven Message; no valid Channel ID found.")        
                            


        else:
            pass 

      
# =======================================================================================================
# === Send Raven Message from received email to users/channels ==
def send_raven_to_email_receiver(doc,method):
   # Check if the email is marked as "Received"
    if doc.sent_or_received == "Received":

        # Fetch all enabled Raven Email Notification Forwarding configurations
        list_of_all_raven_email_notification = frappe.db.get_list('Raven Email Notification Forwarding',filters={"enabled":1},fields=["name","condition_based_on","conditions","channel_or_dm"])

        # If there are any enabled notifications
        if list_of_all_raven_email_notification and len(list_of_all_raven_email_notification) > 0:
            for raven_email in list_of_all_raven_email_notification:
                # Get the Raven Email Notification Forwarding document as a dictionary
                raven_email_doc = frappe.get_doc("Raven Email Notification Forwarding", raven_email.get("name")).as_dict()

                # Process the document if it exists
                if raven_email_doc:
                    if raven_email_doc.get("conditions"):
                        
                        
                        condition = raven_email_doc.get("conditions")
                        # if condition in doc.recipients:
                        if eval(condition):
                            # If the notification type is "Channel"
                            if raven_email_doc.get("channel_or_dm") == "Channel":
                                # Get the list of channel names from the document
                                raven_channels = [channel.get('raven_channel') for channel in raven_email_doc.raven_channel]
                                if raven_channels:
                                    for channel_name in raven_channels:
                                        # Fetch the channel details
                                        channels = frappe.get_all("Raven Channel", filters={"name": channel_name}, fields=["name", "channel_name", "is_direct_message"])
                                        
                                         # Check if the channel is not a direct message channel
                                        if channels and channels[0].get("is_direct_message") == 0:
                                            selected_channel = channels[0].get("name")
                                            raven_message = doc.content
                                            subject = doc.subject 
                                            # Create and send the Raven message to the selected channel
                                            create_and_send_raven_message_for_email_forwarding(doc, subject,selected_channel, raven_message)

                                            
                            # If the notification type is "DM" (Direct Message)
                            else:
                                if raven_email_doc.get("channel_or_dm") == "DM":
                                    # Get the list of user IDs for direct messages
                                    dm_channels = [channel.get('raven_users') for channel in raven_email_doc.dm]
                                    if dm_channels:
                                        for raven_users in dm_channels:
                                            admin_email = doc.sender
                                            # Create a unique channel name for the direct message
                                            channel_name = f"{admin_email} _ {raven_users}"
                                            # Fetch the channel ID if it already exists
                                            channel_id = frappe.db.get_value('Raven Channel', 
                                                {
                                                    "channel_name": channel_name,
                                                    "is_direct_message": 1
                                                }, 
                                                'name'
                                            )
                                            # If the channel does not exist, create a new one
                                            if not channel_id:
                                                channel_doc = frappe.new_doc('Raven Channel')
                                                channel_doc.channel_name = channel_name
                                                channel_doc.is_direct_message = True
                                                channel_doc.is_self_message = False  # Admin is not messaging themselves
                                                channel_doc.save()
                                                frappe.db.commit()
                                                channel_id = channel_doc.name
                                                print(f"Created new Raven Channel with ID: {channel_id}")
                                            else:
                                                print(f"Fetched existing Raven Channel with ID: {channel_id}")
                                            
                                            # Create and send Raven Message
                                            if channel_id:
                                                
                                                
                                                selected_channel = channel_id
                                                raven_message = doc.content
                                                subject =  doc.subject
                                                

                                                create_and_send_raven_message_for_email_forwarding(doc, subject,selected_channel, raven_message)


    return


# this code is for creating message for raven Raven Email Notification Forwarding doctype
# Function to create and send a Raven message for email forwarding
def create_and_send_raven_message_for_email_forwarding(doc, subject,channel, raven_message):
    
    user = frappe.session.user
    action = assign(user,doc)
    
    try:
        # Render the subject with dynamic content based on the 'doc' object
        subject = frappe.render_template(subject, {'doc': doc})
        # Create a new Raven Message document
        raven_message_doc = frappe.new_doc("Raven Message")
        raven_message_doc.text = raven_message
        raven_message_doc.channel_id = channel
        raven_message_doc.save()
        
        frappe.db.commit()
        # Process the message further if needed (implementation assumed)
        process_message(doc, channel, raven_message)
    except Exception as e:
        frappe.msgprint(f"An error occurred while creating or sending the Raven message: {e}")


      

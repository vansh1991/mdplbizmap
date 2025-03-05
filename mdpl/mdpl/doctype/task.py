import frappe
from frappe.core.doctype.communication.email import make
from frappe.utils import today
from urllib.parse import urlparse
from frappe.utils import get_url_to_form

from raven.api.raven_channel import get_channels

# def send_email_on_incomplete_task():

#     task_status = ["Open", "Working", "Pending Review", "Overdue"]
#     incomplete_tasks = frappe.db.get_list('Task', 
#                                      filters={'exp_end_date': ['<', today()], 'status': ('in', task_status)}, 
#                                      fields=['subject', 'name'])
    
#     email_recipients = {}
    
#     for task in incomplete_tasks:
#         todos = frappe.db.get_list('ToDo', 
#                                    filters={'reference_type': 'Task', 'reference_name': task.name}, 
#                                    fields=['allocated_to'])
        
#         for todo in todos:
#             owner_email = frappe.db.get_value('User', todo.allocated_to, 'email')
#             if owner_email:
#                 if owner_email not in email_recipients:
#                     email_recipients[owner_email] = []
#                 email_recipients[owner_email].append(task)
#     link =""
#     for email, tasks in email_recipients.items():
#         # task_list = ''.join([f"<li>{task['subject']}:<a href='{link}{task['name']}'> Go To {task['name']}<a></li>" for task in tasks])
#         # <a href='{link}{task['name']}'> Go To {task['name']}<a>
#         # <a href='{lk}'>Go To {task_name}</a>
        
#         task_list = ""
#         for task in tasks:
#             lk = get_url_to_form('Task', task['name'])
#             # frappe.urllib.get_full_url
#             task_subject = task['subject']
#             task_name = task['name']
#             task_link = f"{link}{task_name}"
#             task_list += f"<li>{task_subject}: {task_name}</li>"



#         User_name=frappe.db.get_value("User",{'email':email},'full_name')    

#         subject = "Incomplete Tasks Notification"
#         message = f"""
#         <p>Dear {User_name},</p>
#         <p>The following task(s) assigned to you are still incomplete and past their expected end date:</p>
#         <p>Here are the tasks listed below:</p>
#         <ul>{task_list}</ul>
#         <p>Please take the necessary actions to complete them.</p>
#         <p>Thank you!</p>
#         """
         
#         make(recipients=[email],
#              sender=frappe.db.get_value("Email Account",{'default_outgoing':1},'email_id'),
#              subject=subject,
#              content=message,
#              doctype='Task',
#              send_email=True,
#              name=tasks[0]['name'])


#         channels = get_channels()        
#         print(len(channels),"==========channels")

#         print(email_recipients,"=============email_recipients")
#         if email_recipients:
#             for raven_user,task in email_recipients.items():
#                 channel = frappe.db.get_value('Raven Channel',
#                     {
#                     "channel_name": 'admin@example.com' + " _ " + raven_user,
#                     # "is_direct_message": 1,
#                     "is_self_message": 'admin@example.com' == raven_user,
#                     },
#                     ['name']
#                     )
#                 if channel:
#                     print(channel,"=======channelchannel")
#                     channel_id = channel
#                     print(channel_id,"=====chanel if")
#                 else:
#                     channel = frappe.new_doc('Raven Channel')
                    
                    
#                     channel.channel_name = 'admin@example.com' + " _ " + raven_user,
#                     channel.is_direct_message = True,
#                     channel.is_self_message = 'admin@example.com' == raven_user,
                    
                    
#                     channel.save()
#                     frappe.db.commit()
#                     channel_id = channel.name
#                     print(channel_id,"=====chanel else")
#                 # channel.insert()
                
#                 channel = 'Administrator'+' _ '+raven_user
#                 rendered_message = message


#                 raven_message_doc = frappe.new_doc("Raven Message")
#                 raven_message_doc.text = rendered_message
               
#                 raven_message_doc.channel_id = channel_id
                
#                 raven_message_doc.save()
    
#     frappe.db.commit()
import frappe
from frappe.core.doctype.communication.email import make
from frappe.utils import today, get_url_to_form
from raven.api.raven_channel import get_channels

def send_email_on_incomplete_task():
    task_status = ["Open", "Working", "Pending Review", "Overdue"]
    incomplete_tasks = frappe.db.get_list('Task', 
        filters={'exp_end_date': ['<', today()], 'status': ('in', task_status)}, 
        fields=['subject', 'name']
    )
    
    email_recipients = {}
    
    for task in incomplete_tasks:
        todos = frappe.db.get_list('ToDo', 
            filters={'reference_type': 'Task', 'reference_name': task.name}, 
            fields=['allocated_to']
        )
        
        for todo in todos:
            owner_email = frappe.db.get_value('User', todo.allocated_to, 'email')
            if owner_email:
                if owner_email not in email_recipients:
                    email_recipients[owner_email] = []
                email_recipients[owner_email].append(task)
    
    link = get_url_to_form('Task', '')  # Base URL for task links
    
    for email, tasks in email_recipients.items():
        task_list = ""
        for task in tasks:
            task_link = f"{link}{task['name']}"
            # task_list += f"<li>{task['subject']}: <a href='{task_link}'>Go To {task['name']}</a></li>"
            task_list += f"<li>{task['subject']}: {task['name']}</li>"
        
        user_name = frappe.db.get_value("User", {'email': email}, 'full_name')    

        subject = "Incomplete Tasks Notification"
        message = f"""
        <p>Dear {user_name},</p>
        <p>The following task(s) assigned to you are still incomplete and past their expected end date:</p>
        <p>Here are the tasks listed below:</p>
        <ul>{task_list}</ul>
        <p>Please take the necessary actions to complete them.</p>
        <p>Thank you!</p>
        """
         
        # Send email to the user
        make(
            recipients=[email],
            sender=frappe.db.get_value("Email Account", {'default_outgoing': 1}, 'email_id'),
            subject=subject,
            content=message,
            doctype='Task',
            send_email=True,
            name=tasks[0]['name']
        )
        
        # Fetch or create Raven Channel for each user
        admin_email = 'admin@example.com'
        channel_name = f"{admin_email} _ {email}"
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
            raven_message_doc = frappe.new_doc("Raven Message")
            raven_message_doc.text = message
            raven_message_doc.channel_id = channel_id
            raven_message_doc.save()
            frappe.db.commit()
            print(f"Created new Raven Message linked to Channel ID: {channel_id}")
        else:
            print(f"Cannot create Raven Message; no valid Channel ID found.")
    
    frappe.db.commit()


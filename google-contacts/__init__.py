#!/usr/sbin/env python3
"""Add/Edit/Remove contacts from Google Contacts"""

#from __future__ import print_function
import tkinter as tk
import logging
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

# Logging format
logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')

class GoogleContactGUI:
    fields = [
        'First Name', 'Last Name', 'Company', 'Email Address', 'Business Phone',
        'Mobile Phone', 'Home Phone'
    ]

    contact_body = {
        'names': [{}],
        'phoneNumbers': [{}, {}, {}],
        'organizations': [{}],
        'emailAddresses': [{}]
    }

    def __init__(self, master):
        self.master = master
        self.master.title("Google Contacts API v0.3")
        self.scopes = ['https://www.googleapis.com/auth/contacts'] # If modifying these scopes, delete the file token.json.
        self.token = 'token.json'
        self.credential = 'credential.json'
        self.service = self.authenticate(self.token)
        self.container = tk.Frame
        self.logger = logging.getLogger('contactGUI')

        # Layout
        self.entries = []
        for field in self.fields:
            self.row = tk.Frame(self.master)
            self.label = tk.Label(self.row, width=15, text=field, anchor='w')
            self.entry = tk.Entry(self.row)
            self.row.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
            self.label.pack(side=tk.LEFT)
            self.entry.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.X)
            self.entries.append((field, self.entry))
        self.create_button = tk.Button(self.master, text='Create Contact',
            command=(lambda s=self.service, e=self.entries: self.create_contact(s, e)))
        self.create_button.pack(side=tk.LEFT, padx=5, pady=5)
        self.quit_button = tk.Button(self.master, text='Quit', command=self.master.quit)
        self.quit_button.pack(side=tk.LEFT, padx=40)

    def authenticate(self, token):
        import os
        if os.path.exists(token):
            cred_store = file.Storage(token)
            credential = cred_store.get()
        if not credential or credential.invalid:
            flow = client.flow_from_clientsecrets(self.credential, self.scopes)
            credential = tools.run_flow(flow, cred_store)
        service = build('people', 'v1', http=credential.authorize(Http()),
            cache_discovery=False)
        return service

    def create_contact(self, service, entries):
        count = 0
        for entry in entries:
            key, value = entry[0], entry[1].get()
            if value is not None:
                if key == 'First Name':
                    self.contact_body['names'][0]['givenName'] = value
                    self.contact_body['names'][0]['displayName'] = value
                elif key == 'Last Name':
                    self.contact_body['names'][0]['familyName'] = value
                    self.contact_body['names'][0]['displayName'] += ' ' + value
                elif key == 'Company':
                    self.contact_body['organizations'][0]['name'] = value
                elif key == 'Email Address':
                    self.contact_body['emailAddresses'][0]['value'] = value
                    self.contact_body['emailAddresses'][0]['type'] = 'work'
                elif key == 'Business Phone':
                    self.contact_body['phoneNumbers'][count]['value'] = value
                    self.contact_body['phoneNumbers'][count]['type'] = 'work'
                    count += 1
                elif key == 'Mobile Phone':
                    self.contact_body['phoneNumbers'][count]['value'] = value
                    self.contact_body['phoneNumbers'][count]['type'] = 'mobile'
                    count += 1
                elif key == 'Home Phone':
                    self.contact_body['phoneNumbers'][count]['value'] = value
                    self.contact_body['phoneNumbers'][count]['type'] = 'home'
                    count += 1
        contact = service.people().createContact(body=self.contact_body)
        contact.execute()
        logging.info('Contact {} created'.format())


if __name__ == '__main__':
    root = tk.Tk()
    contact_gui = GoogleContactGUI(root)
    root.mainloop()
    """
    service = google_auth()
    root = tkinter.Tk()
    root.title('Google Contacts v0.2')
    ents = make_form(root, fields)
    root.bind('<Return>', (lambda event, s=service, e=ents: create_contact(s, e)))
    b1 = tkinter.Button(root, text='Create Contact', command=(lambda s=service, e=ents: create_contact(s, e)))
    b1.pack(side=tkinter.LEFT, padx=5, pady=5)
    b2 = tkinter.Button(root, text='Quit', command=root.quit)
    b2.pack(side=tkinter.LEFT, padx=5, pady=5)
    root.mainloop()
    """
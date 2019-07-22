#!/usr/sbin/env python3
"""Add/Edit/Remove contacts from Google Contacts"""

#from __future__ import print_function
from __future__ import print_function
import pickle
import os.path
import tkinter as tk
import logging
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
#from httplib2 import Http

# Logging format
logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')

class GoogleContactGUI:
    fields = [
        'First Name', 'Last Name', 'Company', 'Email Address', 'Business Phone',
        'Mobile Phone', 'Home Phone'
    ]

    def __init__(self, master):
        self.master = master
        self.master.title("Google Contacts API v0.3")
        # If modifying these scopes, delete the file token.json.
        self.scopes = ['https://www.googleapis.com/auth/contacts']
        self.credentials = 'credentials.json'
        self.service = self._authenticate(self.credentials)
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
            command=(lambda s=self.service, e=self.entries: self._create_contact(s, e)))
        self.create_button.pack(side=tk.LEFT, padx=5, pady=5)
        self.quit_button = tk.Button(self.master, text='Quit', command=self.master.quit)
        self.quit_button.pack(side=tk.LEFT, padx=40)

    def _authenticate(self, cred_file):
        """Authenticate against Google Contact API"""
        creds = None
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    cred_file, self.scopes)
                creds = flow.run_local_server(port=0)
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        service = build('people', 'v1', credentials=creds, cache_discovery=False)
        return service

    def _create_contact(self, service, entries):
        contact_body = self._fill_form(entries)
        contact = service.people().createContact(body=contact_body)
        contact.execute()
        logging.info('Contact created successfully')

    def _fill_form(self, entries):
        """Fills in the contact body with info from Tkinter fields"""
        contact_body = {
            'names': [{}],
            'phoneNumbers': [{}, {}, {}],
            'organizations': [{}],
            'emailAddresses': [{}]
        }
        count = 0
        for entry in entries:
            key, value = entry[0], entry[1].get()
            if value is not None:
                if key == 'First Name':
                    contact_body['names'][0]['givenName'] = value
                    contact_body['names'][0]['displayName'] = value
                elif key == 'Last Name':
                    contact_body['names'][0]['familyName'] = value
                    contact_body['names'][0]['displayName'] += ' ' + value
                elif key == 'Company':
                    contact_body['organizations'][0]['name'] = value
                elif key == 'Email Address':
                    contact_body['emailAddresses'][0]['value'] = value
                    contact_body['emailAddresses'][0]['type'] = 'work'
                elif key == 'Business Phone':
                    contact_body['phoneNumbers'][count]['value'] = value
                    contact_body['phoneNumbers'][count]['type'] = 'work'
                    count += 1
                elif key == 'Mobile Phone':
                    contact_body['phoneNumbers'][count]['value'] = value
                    contact_body['phoneNumbers'][count]['type'] = 'mobile'
                    count += 1
                elif key == 'Home Phone':
                    contact_body['phoneNumbers'][count]['value'] = value
                    contact_body['phoneNumbers'][count]['type'] = 'home'
                    count += 1
        return contact_body


if __name__ == '__main__':
    root = tk.Tk()
    contact_gui = GoogleContactGUI(root)
    root.mainloop()
    
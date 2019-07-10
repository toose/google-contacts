#!/usr/sbin/env python3
"""Add/Edit/Remove contacts from Google Contacts"""

from __future__ import print_function
import tkinter, logging
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

# Logging format
#logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')

# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/contacts'

fields = 'First Name', 'Last Name', 'Company', 'Email Address', 'Business Phone', 'Mobile Phone', 'Home Phone'

contact_body = {
    'names': [{}],
    'phoneNumbers': [{}, {}, {}],
    'organizations': [{}],
    'emailAddresses': [{}]
}

def google_auth():
    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('people', 'v1', http=creds.authorize(Http()))
    service.people()
    return service


def create_contact(service, entries_list):
    count = 0
    for entry in entries_list:
        key, value = entry[0], entry[1].get()
        if value is not None:
            if key == 'First Name':
                contact_body['names'][0]['givenName'] = value
                contact_body['names'][0]['displayName'] = value
            elif key == 'Last Name':
                contact_body['names'][0]['familyName'] = value
                contact_body['names'][0]['displayName'] += ' ' + value
            #contact_body['names'][0]['displayNameLastFirst'] = entries_list[i] + ' ' + entries_list[i - 1]
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
    contact = service.people().createContact(body=contact_body)
    contact.execute()
    logging.info('Contact created')


def fetch(entries):
    for entry in entries:
        field = entry[0]
        text = entry[1].get()
        print('%s: "%s"' % (field, text))


def make_form(root, fields):
    entries = []
    for field in fields:
        row = tkinter.Frame(root)
        lab = tkinter.Label(row, width=15, text=field, anchor='w')
        ent = tkinter.Entry(row)
        row.pack(side=tkinter.TOP, fill=tkinter.X, padx=5, pady=5)
        lab.pack(side=tkinter.LEFT)
        ent.pack(side=tkinter.RIGHT, expand=tkinter.YES, fill=tkinter.X)
        entries.append((field, ent))
    return entries


if __name__ == '__main__':
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
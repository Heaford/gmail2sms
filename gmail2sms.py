from __future__ import print_function
import httplib2
import sys,os
from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools
import messagebird

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/gmail-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/gmail.modify'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Gmail API Python Quickstart'
# https://developers.google.com/gmail/api/quickstart/python#troubleshooting
# Follow Step 1 to obtain Credentials file and move it to your working directory. 


MESSAGEBIRD_ACCESS_KEY = 'youraccesskey'
# https://www.messagebird.com/en-gb/
# Create an account and copy the access key into the above string

LABEL_ID = 'Label_15'
# https://developers.google.com/gmail/api/v1/reference/users/labels/list?authuser=
# to find the label id you wish to use, goto the above url, click 'try it now' and enter your email address in the userID field.

def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'gmail-python-quickstart.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def ModifyMessage(service, user_id, msg_id, msg_labels):
  """Modify the Labels on the given Message.

  Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    msg_id: The id of the message required.
    msg_labels: The change in labels.

  Returns:
    Modified message, containing updated labelIds, id and threadId.
  """
  try:
    message = service.users().messages().modify(userId=user_id, id=msg_id,
                                                body=msg_labels).execute()

    label_ids = message['labelIds']

    print ('Message ID: %s - With Label IDs %s' % (msg_id, label_ids))
    return message
  except errors.HttpError, error:
    print ('An error occurred: %s' % error)



def ListMessagesWithLabels(service, user_id, query='', label_ids=[], ):
  """List all Messages of the user's mailbox with label_ids applied.

  Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    label_ids: Only return Messages with these labelIds applied.
    query: any query to be run with the list such as 'is:unread'

  Returns:
    List of Messages that have all required Labels applied. Note that the
    returned list contains Message IDs, you must use get with the
    appropriate id to get the details of a Message.
  """

  try:
    response = service.users().messages().list(userId=user_id,
                                               labelIds=label_ids,
                                               q=query).execute()
    messages = []
    if 'messages' in response:
      messages.extend(response['messages'])

    while 'nextPageToken' in response:
      page_token = response['nextPageToken']
      response = service.users().messages().list(userId=user_id,
                                                 labelIds=label_ids,
                                                 pageToken=page_token).execute()
      messages.extend(response['messages'])

    return messages
  except errors.HttpError, error:
    print('An error occurred: %s' % error)

def markEmailsasUnread(service):
    labelsToRemove = {
    "addLabelIds": [],
    "removeLabelIds": ['UNREAD']}

    MessageResults = ListMessagesWithLabels(service,'me','is:unread',LABEL_ID)
    for individualMessage in MessageResults:
        ModifyMessage(service,'me', individualMessage['id'], {'removeLabelIds': ['UNREAD'], 'addLabelIds': []})

def sendSMSAlert():
    client = messagebird.Client(MESSAGEBIRD_ACCESS_KEY)
    try:
        msg = client.message_create('FromMe', '+447789908834', 'Hello Chief, You have an unread email', { 'reference' : 'Foobar' })
        print("SMS Sent")
    except messagebird.client.ErrorException as e:
        print('\nAn error occured while requesting a Message object:\n')

        for error in e.errors:
            print('  code        : %d' % error.code)
            print('  description : %s' % error.description)
            print('  parameter   : %s\n' % error.parameter)


def main():
    """Shows basic usage of the Gmail API.

    Creates a Gmail API service object and outputs a list of label names
    of the user's Gmail account.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)

    results = service.users().labels().get(userId='me',id=LABEL_ID).execute()
    print ("Number of unread emails: %d" % results['threadsUnread'])

    if results['threadsUnread'] > 0:
        markEmailsasUnread(service)
        sendSMSAlert()
    else:
        print("no unread messages")


    



if __name__ == '__main__':
    main()
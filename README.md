Digitaleo-api-python
===================


Python wrapper around the Digitaleo's API 

----------

Installation
-------------

```bash
pip install https://github.com/digitaleo/Digitaleo-api-python/
```

Usage
-------------


```python
# Import auth and API modules
from digitaleo.auth import OAuth2
from digitaleo.api import API

# Instantiate auth object
auth = OAuth2(client_id="YOUR CLIENT ID", 
			  client_secret="YOUR CLIENT SECRET")

# Instantiate a generic API object
api = API(
	url='https://contacts.messengeo.net/rest',
	resource='contacts',
	auth=auth)

# Get a resource
print api.read(params={'id': 12345678})

# Update a contact
print api.update(
    params={
        'metaData' : {'lastName': "Bar"},
        'id': 12345678
    })

# Import contact list
contact_file = 'contacts.csv'
print api.post(
	params={'action': 'import'},
	files={'contactFile': open(contact_file, 'rb')})

# Change the resource:
api.resource = 'lists'
print api.read(params={'id': 56789})

# Change the resource and the url
api.url = 'https://api.messengeo.net/rest'
api.resource = 'campaigns'

# Create a campaign
campaignToCreate = {
  'name':'Test campaign',
  'listId':133201,
  'steps':[
     {
        'mode':'combined',
        'date':'2037-09-20 12:00:00',
        'mailings':[

           {
               'name' : 'mailing email du 2 juillet',
               'text' : 'Bientot les soldes',
               'html' : '<html><head>Titre de la page</head><body>Bientot les soldes #OPTOUTLINK#</body></html>',
               'subject' : 'Info soldes',
               'replyContact' : 'sender@gmail.com',
              'media':'EMAIL'
           },{
              'name' : 'mailing sms du 2 juillet',
              'text' : 'Bientot les soldes',
              'media' : 'SMS'
          }

        ]
     }
  ]
}
print api.post(params=campaignToCreate)

# Get a campaign
print api.read(params={'limit': 1, 'sort' : 'id DESC', 'properties' : 'id,name'})
```

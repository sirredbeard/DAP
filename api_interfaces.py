
def api_plpl(defendant_name):

    # submit api call to plpl using defendant name, city columbus, county muscogee, state georgia

    # code snippets
    # https://docs.pipl.com/docs/code-snippets

    # python library
    # https://docs.pipl.com/docs/code-libraries#section-python

    # get first match back, which is the most likely candidate, ignore multiple matches for now
    # if a match from plpl, set match_true = true, populate return variables with data from ppl
    # if no match from plpl, set met_true = false, leave other return variables blank

    from api_keys import plpl_api_key
    from piplapis.search import SearchAPIRequest
    from piplapis.data import Person, Name, Address
    from piplapis.search import SearchAPIError

    SearchAPIRequest.set_default_settings(api_key=plpl_api_key, minimum_probability=0.9, use_https=True)
    
    fields = [Name(first=u'First', last=u'Last'),
          Address(country=u'US', state=u'GA', city=u'Columbus')
          ]
    
    request = SearchAPIRequest()

    try:
        response = request.send()
        match_true = true

        # parse address, https://docs.pipl.com/reference#address

        address = response.address
        defendant_street = address.state
        defendant_city = address.city
        defendant_state = address.state
        defendant_zip = address.zip_code
        defendant_address_type = address.type

             # ! reject any address marked as 'work' address and return no mail address
             # if address.type == "work" ...

        # parse e-mail, see https://docs.pipl.com/reference#email

        email = response.email

            # ! reject any e-mail marked as 'work' e-mail and return no e-mail address
    
        # parse facebook, see see https://docs.pipl.com/reference#user-id

        usernames = response.usernames                

            # ! parse user_ids into defendant_facebook

        # ! log any api error messages with request to plpl.log

    except SearchAPIError as e:
        print e.http_status_code, 

    return match_true, defendant_street, defendant_city, defendant_state, defendant_zip, defendant_email, defendant_facebook

def api_lob(court_name, case_number_, date_filed, plaintiff_name, defendant_name, defendant_street, defendant_city, defendant_state, defendant_zip)
    
    # api documentation
    # https://lob.com/docs/python#letters_create

    # python library    
    # https://github.com/lob/lob-python

    # adapted from sample code:

    import lob
    from api_keys import lob.api_key

    lob.Letter.create(
    description = 'Bankruptcy Letter',
    to_address = {
        'name': defendant_name,
        'address_line1': defendant_street,
        'address_city': defendant_city,
        'address_state': defendant state,
        'address_zip': defendant_zip
    },
    from_address = '', # ID of a return address saved in lob account
    file = '',  # ID of an HTML template saved in lob account, uses merge variables from below
                # see guide https://lob.com/resources/guides/general/templates
                # use simple template like https://lob.com/resources/template-gallery/failed-payment-notice-letter-template/gtmpl_962f66c6ba95bd
    merge_variables = {
        'defendant_name': defendant_name
        'plaintiff_name': plaintiff_name
        'court_name': court_name
        'case_number': case_number
        'date_filed': date_filed
    },
    color = True
    )

    return 0

def api_clicksend(court_name, case_number_, date_filed, plaintiff_name, defendant_name, defendant_email)

    # https://developers.clicksend.com/docs/rest/v3/?python#ClickSend-v3-API-Transactional-Email

    # adapted from sample code:
    
    import time
    import clicksend_client
    from clicksend_client.rest import ApiException
    from pprint import pprint

    configuration = clicksend_client.Configuration()

    from api_keys import configuration.username, configuration.username

    api_instance = clicksend_client.TransactionalEmailApi(clicksend_client.ApiClient(configuration))
    email_receipient=EmailRecipient(email=defendant_email,name=defendant_name)
    email_from=EmailFrom(email_address_id='',name='')
    email = clicksend_client.Email(to=[defendant_email],
                                    bcc=[email_receipient], # send to storage e-mail account for arching
                                    _from=[email_from],
                                    subject="Legal Advertising: Debt Collection Lawsuit Filed In Muscogee County",
                                    body="A lawsuit may have been filed against you, let us help you.") # I have a ticket open with clicksend about how best to format body.
    try:
        api_response = api_instance.email_send_post(email)
        print(api_response)
    except ApiException as e:
        print("Exception when calling TransactionalEmailApi->email_send_post: %s\n" % e)

        return 0

def api_facebook(court_name, case_number_, date_filed, plaintiff_name, defendant_name,defendant_facebook)

    # https://fbchat.readthedocs.io/en/latest/intro.html

    from fbchat import Client
    from fbchat.models import *
    from api_keys import facebook_email, facebook_password

    client = Client(facebook_email, facebook_password)
    client.send(Message(text="Message"), thread_id=client.uid, thread_type=ThreadType.USER)

    return 0
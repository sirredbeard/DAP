def api_pipl(defendant_name):
    # submit api call to pipl using defendant name, city columbus, county muscogee, state georgia

    # code snippets
    # https://docs.pipl.com/docs/code-snippets

    # python library
    # https://docs.pipl.com/docs/code-libraries#section-python

    # get first match back, which is the most likely candidate, ignore multiple matches for now
    # if a match from pipl, set match_true = true, populate return variables with data from ppl
    # if no match from pipl, set met_true = false, leave other return variables blank

    # adapted from sample code:

    from api_keys import pipl_api_key
    from piplapis.search import SearchAPIRequest
    from piplapis.search import SearchAPIResponse
    from piplapis.search import SearchAPIError
    from piplapis.data import Person, Name, Address

    SearchAPIRequest.set_default_settings(api_key=pipl_api_key, minimum_probability=0.8,
                                          use_https=True)  # use encrypted connection and ensure 80% probability matching

    # parse defendant_name into defendant_first_name, defendant_middle_name, and defendant_last_name
    defendant_last_name, defendant_first_name, defendant_middle_name = defendant_name.split(' ', 2)

    name = Name(first="defendant_first_name", middle="defendant_middle_name", last="defendant_last_name")

    fields = [Name(first=defendant_first_name, middle=defendant_middle_name, last=defendant_last_name),
              Address(country=u'US', state=u'GA', city=u'Columbus')
              # all cases on this mainframe will be located here, so we can hardcode these
              ]

    # for debugging
    print(fields)

    request = SearchAPIRequest(person=Person(fields=fields))

    # for debugging
    print(request)

    # ! log api messages to pipl.log

    try:
        response = request.send()
        match_true = True

        # for debugging
        print(response.person)

        # ! need to parse address, https://docs.pipl.com/reference#address

        address = response.person.address
        defendant_street = address.state
        defendant_city = address.city
        defendant_state = address.state
        defendant_zip = address.zip_code
        defendant_address_type = address.type

        # ! reject any address marked as 'work' address and record a note of this in compliance.log
        # if address.type == "work" ...

        # parse e-mail, see https://docs.pipl.com/reference#email

        defendant_email = response.email

        # ! reject any e-mail marked as 'work' e-mail and record a note of this in compliance.log

        # parse facebook, see see https://docs.pipl.com/reference#user-id

        defendant_facebook = response.usernames

        # ! parse user_ids containing "@facebook" into defendant_facebook

    except SearchAPIError as e:
        print(e.http_status_code)
        match_true = False

    return match_true, defendant_street, defendant_city, defendant_state, defendant_zip, defendant_email, defendant_facebook


def api_lob(court_name, case_number, date_filed, plaintiff_name, defendant_name, defendant_street, defendant_city,
            defendant_state, defendant_zip):
    # api documentation
    # https://lob.com/docs/python#letters_create

    # python library    
    # https://github.com/lob/lob-python

    # adapted from sample code:

    from api_keys import lob_api_key

    import lob

    letter = lob.Letter.create(
        description='Bankruptcy Letter',
        to_address={
            'name': defendant_name,
            'address_line1': defendant_street,
            'address_city': defendant_city,
            'address_state': defendant_state,
            'address_zip': defendant_zip
        },
        from_address='',  # ID of a return address saved in lob account
        file='',  # ID of an HTML template saved in lob account, uses merge variables from below
        # see guide https://lob.com/resources/guides/general/templates
        # use simple template like https://lob.com/resources/template-gallery/failed-payment-notice-letter-template/gtmpl_962f66c6ba95bd
        merge_variables={
            'defendant_name': defendant_name,
            'plaintiff_name': plaintiff_name,
            'court_name': court_name,
            'case_number': case_number,
            'date_filed': date_filed
        },
        color=True
    )

    # log api responses to lob.log

    return 0


def api_clicksend(court_name, case_number, date_filed, plaintiff_name, defendant_name, defendant_email):
    # https://developers.clicksend.com/docs/rest/v3/?python#ClickSend-v3-API-Transactional-Email

    # adapted from sample code:

    import clicksend_client
    from clicksend_client.rest import ApiException

    from clicksend_client import EmailRecipient
    from clicksend_client import EmailFrom
    from clicksend_client import Attachment

    configuration = clicksend_client.Configuration()

    from api_keys import configuration_username, configuration_password

    api_instance = clicksend_client.TransactionalEmailApi(clicksend_client.ApiClient(configuration))
    email_recipient = EmailRecipient(email=defendant_email, name=defendant_name)
    email_from = EmailFrom(email_address_id='', name='')
    email = clicksend_client.Email(to=[defendant_email],
                                   bcc=[email_recipient],  # send to storage e-mail account for arching
                                   _from=[email_from],
                                   subject="Legal Advertising: Debt Collection Lawsuit Filed In Muscogee County",
                                   body="A lawsuit may have been filed against you, let us help you.")  # I have a ticket open with clicksend about how best to format body.
    try:
        api_response = api_instance.email_send_post(email)
        print(api_response)
        # ! record clicksend api response to clicksend.log
    except ApiException as e:
        print("Exception when calling TransactionalEmailApi->email_send_post: %s\n" % e)

        return 0


def api_facebook(court_name, case_number, date_filed, plaintiff_name, defendant_name, defendant_facebook):
    # https://fbchat.readthedocs.io/en/latest/intro.html

    # adapted from sample code:

    from fbchat import Client
    import fbchat.models
    from api_keys import facebook_email, facebook_password

    client = Client(facebook_email, facebook_password)
    client.send(fbchat.models.Message(text="Message"), thread_id=client.uid,
                thread_type=fbchat.models.ThreadType.USER)
    # ! record facebook response to facebook.log

    return 0

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
    defendant_last_name, defendant_middle_name, defendant_first_name = defendant_name.split(' ', 2)

    fields = [Name(first=defendant_first_name, middle=defendant_middle_name, last=defendant_last_name),
              Address(country=u'US', state=u'GA', city=u'Columbus')  # all cases on this mainframe will be located here, so we can hardcode these
              ]

    # for debugging
    print (fields)

    request = SearchAPIRequest(person=Person(fields=fields), api_key=pipl_api_key)

    # for debugging
    print (request)

    # TODO: log api messages to pipl.log

    # create return object + set default state
    defendant = {}
    defendant["match_true"] = False

    try:
        # try fetching a request
        response = request.send()
    except SearchAPIError as e:
        print(e.http_status_code)

    if response.person:
        # direct match found!
        person = response.person

    elif len(response.possible_persons) > 0:
        # TODO: possible matches, need to parse
        print("possible_persons > 0") # placeholder

    if person:
        # TODO: catch index exceptions thrown in case of empty arrays?

        # a match was found!
        defendant["match_true"] = True

        # for debugging
        print (person.__dict__)

        # set default values before parsing person object
        street = ""
        state = ""
        city = ""
        zip = ""
        type = ""
        email_addrs = ""
        facebook = ""

        # parse addresses, see https://docs.pipl.com/reference#address

        last_seen = None
        for address in person.addresses:
            # look for most recently seen among addresses

            if address.type and address.type == "work":
                # TODO: record a note to compliance.log
                continue

            if address.last_seen:
                # address has last_seen date, set as latest or compare
                if not last_seen or address.last_seen > last_seen:
                    last_seen = address_last_seen
                    street = address.street ? address.street : ""
                    state = address.state ? address.state : ""
                    city = address.city ? address.city : ""
                    zip = address.zip ? address.zip : ""
                    type = address.type ? address.type : ""

        # parse emails, https://docs.pipl.com/reference#email

        for email in person.emails:
            # TODO: handle multiple personal emails? by default
            #       value of type is personal

            if email.type and email.type == "work":
                # TODO: record a note to compliance.log
                continue

            email_addrs = email

        # parse facebook, see see https://docs.pipl.com/reference#user-id

        for id in person.user_ids:
            # TODO: handle case of multiple facebook accounts?

            if id.content and id.content.endswith("@facebook"):
                facebook = id.content[0:-9] # remove the '@facebook'

        # set all parsed values
        defendant["street"] = street
        defendant["city"] = city
        defendant["state"] = state
        defendant["zip"] = zip_code
        defendant["email"] = email_addrs
        defendant["facebook"] = facebook

    return defendant


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

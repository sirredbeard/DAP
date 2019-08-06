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

    # create return object + set default state
    defendant = {}
    defendant["match_true"] = False

    SearchAPIRequest.set_default_settings(api_key=pipl_api_key, minimum_probability=0.8,
                                          use_https=True)  # use encrypted connection and ensure 80% probability matching

    # Split name supplied into values parsable by request api
    names = defendant_name.split(' ')
    defendant_last_name = names[0]
    defendant_middle_name = "" # ensures always initialized

    # handle cases 2, 3 or more total names
    if len(names) == 2:
        defendant_first_name = names[1]
    elif len(names) == 3:
        defendant_middle_name = names[1]
        defendant_first_name = names[2]
    else:
        # TODO: handle >3 names
        print("Invalid name format")
        return defendant

    fields = [Name(first=defendant_first_name, middle=defendant_middle_name, last=defendant_last_name),
              Address(country=u'US', state=u'GA', city=u'Columbus')  # all cases on this mainframe will be located here,
              ]

    # for debugging
    print (fields)

    # prepare request
    request = SearchAPIRequest(person=Person(fields=fields), api_key=pipl_api_key)

    # for debugging
    print (request)

    # TODO: log api messages to pipl.log

    # assures that reference is assigned before later access
    response = None
    person = None

    # try fetching a request
    try:
        response = request.send()
    except SearchAPIError as e:
        print(e.http_status_code)
        print(e.__dict__)

    # direct match found!
    if response and response.person:
        person = response.person

    # possible matches found, pick most likely candidate
    elif response and len(response.possible_persons) > 0:
        locals = list()

        for person in response.possible_persons:
            local_addresses = get_matching_addresses(addresses = person.addresses,
                                                                 city = "Columbus",
                                                                 state = "GA")

            # Person is a local resident, add them to list of locals
            if local_addresses > 0: locals.append(person)

        # placeholder for further processing
        if len(locals) > 0: person = locals[0]

    # none found or empty response
    else:
        # for debugging
        if not response: print("Error: empty response")
        else: print("No matches found")

    if person:
        # TODO: catch index exceptions thrown in case of empty arrays?

        # a match was found!
        defendant["match_true"] = True

        # set default values before parsing person object
        defendant_addres = None
        defendant_email = ""
        defendant_facebook = ""

        # parse addresses, see https://docs.pipl.com/reference#address

        # Get addresses from within Columbus, GA
        addresses = get_matching_addresses(addresses = person.addresses,
                                           city = "Columbus",
                                           state = "GA")

        # for matching addresses within the state find latest (if > 1)
        last_seen = None
        for address in addresses:

            # Skip if old, skip if work and record to compliance log, default type is home
            if address.type:
                if address.type == "work":
                    # TODO: record a note to compliance.log
                    print("work address") # placeholder
                elif address.type "old":
                    continue

            # if no last_seen on any address supplied, pick first from array
            # and set last_seen to unix epoch (so any last_seen is bigger)
            if not last_seen:
                last_seen = datetime.datetime.utcfromtimestamp(0)
                defendant_address = address

            # address has last_seen date, compare to set as latest
            if address.last_seen:
                if not last_seen or address.last_seen > last_seen:
                    last_seen = address.last_seen
                    defendant_address = address

        # parse emails, https://docs.pipl.com/reference#email

        for email in person.emails:
            # TODO: handle multiple personal emails? by default
            #       value of type is personal

            if email.type and email.type == "work":
                # TODO: record a note to compliance.log
                continue

            defendant_email = email.address

        # parse facebook, see see https://docs.pipl.com/reference#user-id

        for id in person.user_ids:
            # TODO: handle case of multiple facebook accounts?

            if id.content and id.content.endswith("@facebook"):
                defendant_facebook = id.content[0:-9] # remove the '@facebook'

        # set all parsed values
        defendant["street"] = defendant_address.street if defendant_address.street else ""
        defendant["city"] = defendant_address.city if defendant_address.city else ""
        defendant["state"] = defendant_address.state if defendant_address.state else ""
        defendant["zip"] = defendant_address.zip_code if defendant_address.zip_code else ""
        defendant["email"] = defendant_email
        defendant["facebook"] = defendant_facebook

    print(defendant)

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

from dap_logging import dap_log, LogType, LogLevel


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

    from api_keys import pipl_social_api_key, pipl_biz_api_key
    from piplapis.search import SearchAPIRequest
    from piplapis.search import SearchAPIResponse
    from piplapis.search import SearchAPIError
    from piplapis.data import Person, Name, Address
    import pipl_processing
    import datetime

    # create return object + set default state
    defendant = {"match_true": False}

    SearchAPIRequest.set_default_settings(api_key=pipl_social_api_key, minimum_probability=0.8,
                                          use_https=True)  # use encrypted connection and ensure 80% probability matching

    # Split name supplied into values parsable by request api
    names = defendant_name.split(' ')
    defendant_last_name = names[0]
    defendant_middle_name = ""  # ensures always initialized

    # handle cases 2, 3 or more total names
    if len(names) == 2:
        defendant_first_name = names[1]
    elif len(names) == 3:
        defendant_middle_name = names[2]
        defendant_first_name = names[1]
    else:
        # TODO: handle >3 names
        print("Invalid name format")
        return defendant

    fields = [Name(first=defendant_first_name, middle=defendant_middle_name, last=defendant_last_name),
              Address(country=u'US', state=u'GA', city=u'Columbus')  # all cases on this mainframe will be located here,
              ]

    # prepare request
    request = SearchAPIRequest(person=Person(fields=fields), api_key=pipl_social_api_key)

    # for debugging
    dap_log_pipl(LogLevel.DEBUG, str(request.__dict__))

    # TODO: log api messages to pipl.log

    # assures that reference is assigned before later access
    response = None
    person = None

    # try fetching a request
    try:
        response = request.send()
    except SearchAPIError as e:
        message = "SearchAPIError: %i: %s" % (e.http_status_code, e.error)
        dap_log_pipl(LogLevel.CRITICAL, message)

    # direct match found!
    if response and response.person:
        dap_log_pipl(LogLevel.DEBUG, "direct match!")
        person = response.person

    # possible matches found, pick most likely candidate
    elif response and len(response.possible_persons) > 0:
        dap_log_pipl(LogLevel.DEBUG, "possible matches, searching...")

        local_list = list()
        for possible in response.possible_persons:
            local_addresses = pipl_processing.get_matching_addresses(addresses=possible.addresses,
                                                                     city="Columbus",
                                                                     state="GA")

            # Person is a local resident, add them to list of local_list
            if len(local_addresses) != 0:
                local_list.append(possible)

        # TODO: pick from last or possible persons, placeholder for further processing
        if len(local_list) != 0:
            dap_log_pipl(LogLevel.DEBUG, "match found!")
            person = local_list[0]

    # no match found or empty response
    else:
        if not response:
            message = "Empty response!"
            dap_log_pipl(LogLevel.ERROR, message)
        else:
            message = "No matching person found for %s." % defendant_name
            dap_log_pipl(LogLevel.WARN, message)

    if person:
        dap_log_pipl(LogLevel.DEBUG, str(person.__dict__))

        # TODO: catch index exceptions thrown in case of empty arrays?
        
        # a match was found!
        defendant["match_true"] = True

        # set default values before parsing person object
        defendant_house = None
        defendant_address = None
        defendant_apartment = None
        defendant_email = ""
        defendant_facebook = ""

        # parse addresses, see https://docs.pipl.com/reference#address

        # Get addresses from within Columbus, GA
        addresses = pipl_processing.get_matching_addresses(addresses=person.addresses,
                                                           city="Columbus",
                                                           state="GA")

        # for matching addresses within the state find latest (if > 1)
        last_seen = None
        for address in addresses:
            # This is the marked current address, break out of loop
            if address.current and address.current == True:
                defendant_address = address
                break

            # Skip if old, skip if work and record to compliance log, default type is home
            if address.type:
                if address.type == "work":
                    # TODO: record a note to compliance.log
                    message = "Work address found for %s, skipping." % defendant_name
                    dap_log_pipl(LogLevel.INFO, message)
                elif address.type == "old":
                    continue

            # address has last_seen date, compare to set as latest
            if address.last_seen:
                if not last_seen or address.last_seen >= last_seen:
                    last_seen = address.last_seen
                    defendant_address = address

            # if no last_seen on any address supplied, pick first from array
            # and set last_seen to unix epoch (so any last_seen is bigger)
            else:
                if not defendant_address:
                    last_seen = datetime.datetime.utcfromtimestamp(0)
                    defendant_address = address

        # TODO:
        #   if a general search with the pipl_social_api_key returns defendant_email as "full.email.available@business.subscription"
        #   then do a follow-up search with the pipl_biz_api_key to get the e-mail address

        last_seen = None
        for email in person.emails:
            # This is the current email, break out of loop
            if email.current and email.current == True:
                defendant_email = email.address
                break

            # Skip if work email and record to compliance log, default type
            # if omitted is personal
            if email.type and email.type == "work":
                message = "Work email found for %s, skipping." % defendant_name
                dap_log_pipl(LogLevel.INFO, message)
                continue

            # email has last_seen date, compare to set as latest
            if email.last_seen:
                if not last_seen or email.last_seen >= last_seen:
                    last_seen = address.last_seen
                    defendant_email = email.address

            # if no last_seen on any email supplied, pick first from array
            # and set last_seen to unix epoch (so any last_seen is bigger)
            else:
                if not defendant_email:
                    last_seen = datetime.datetime.utcfromtimestamp(0)
                    defendant_email = email.address

        # parse facebook, see see https://docs.pipl.com/reference#user-id

        last_seen = None
        for id in person.user_ids:
            # empty id or not a facebook id, continue through loop
            if not id.content or not id.content.endswith("@facebook"):
                continue

            # email has last_seen date, compare to set as latest
            if id.last_seen:
                if not last_seen or id.last_seen >= last_seen:
                    last_seen = id.last_seen
                    defendant_facebook = id.content[0:-9]  # remove '@facebook'

            # if no last_seen on any email supplied, pick first from array
            # and set last_seen to unix epoch (so any last_seen is bigger)
            else:
                if not defendant_facebook:
                    last_seen = datetime.datetime.utcfromtimestamp(0)
                    defendant_facebook = id.content[0:-9]  # remove '@facebook'

        # set all parsed values
        if not defendant_address: defendant_address = Address()
        defendant["house"] = defendant_address.house if defendant_address.house else ""
        defendant["street"] = defendant_address.street if defendant_address.street else ""
        defendant["apartment"] = defendant_address.apartment if defendant_address.apartment else ""
        defendant["city"] = defendant_address.city if defendant_address.city else ""
        defendant["state"] = defendant_address.state if defendant_address.state else ""
        defendant["zip"] = defendant_address.zip_code if defendant_address.zip_code else ""
        defendant["email"] = defendant_email
        defendant["facebook"] = defendant_facebook

    return defendant


def api_lob(court_name, case_number, date_filed, plaintiff_name, defendant_name, defendant_house, defendant_street, defendant_apt, defendant_city,
            defendant_state, defendant_zip):

    # api documentation
    # https://lob.com/docs/python#letters_create

    # python library    
    # https://github.com/lob/lob-python

    import datetime
    from api_keys import lob_api_key
    import lob

    lob.api_key = lob_api_key
    d = datetime.datetime.today()

    # split and reorganize defendant_name into first, middle, last
    print("Sending letter to:", defendant_name)
    names = defendant_name.split(' ')
    defendant_last_name = names[0]
    defendant_middle_name = ""
    if len(names) == 2:
        defendant_name = names[1] + " " + names[0]
    elif len(names) == 3:
        defendant_name = names[1] + " " + names[2] + " " + names[0]
    else:
        print("Invalid name format")
        return defendant_name

    # convert 

    if defendant_apt == "":
        address_line1 = defendant_house + " " + defendant_street
    else:
        address_line1 = defendant_house + " " + defendant_street + " " + defendant_apt

    print(address_line1)

    try:
        print("Creating letter...")
        letter = lob.Letter.create(
            description='Bankruptcy Letter',
            to_address={
                'name': defendant_name,
                'address_line1': address_line1,
                'address_city': defendant_city,
                'address_state': defendant_state,
                'address_zip': defendant_zip
            },
            from_address='adr_a35f94ee46742f37',  # ID of a return address saved in lob account
            file='tmpl_e5ad54069175664',  # ID of an HTML template saved in lob account, uses merge variables from below
            # see guide https://lob.com/resources/guides/general/templates
            # use simple template like https://lob.com/resources/template-gallery/failed-payment-notice-letter-template/gtmpl_962f66c6ba95bd
            merge_variables={
                'defendant_name': defendant_name,
                'defendant_name_normalized' : str.title(defendant_name),
                'plaintiff_name': plaintiff_name,
                'plaintiff_name_normalized': str.title(plaintiff_name),
                'court_name': court_name,
                'case_number': case_number,
                'date_filed': date_filed,
                'date_filed_year': date_filed[-2:],
                'todays_date': d.strftime('%-m/%-d/%Y'),
            },
            color=True
        )
    except Exception as e:
        dap_log_lob(LogLevel.ERROR, str(e))
        return {"success": False}
    else:
        dap_log_lob(LogLevel.INFO,
                f"id={letter['id']}, expected_delivery_date={letter['expected_delivery_date']}, " +
                f"tracking_number={letter['tracking_number']}")
        mail_results = {"success": True}
        mail_results.update(letter)
        return mail_results


def api_clicksend(court_name, case_number, date_filed, plaintiff_name, defendant_name, defendant_email):
    # https://developers.clicksend.com/docs/rest/v3/?python#ClickSend-v3-API-Transactional-Email

    # to get e-mail address from pipl API, need to upgrade pipl api key from social to business level (leave at social until turn on e-mail)

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
    email_from = EmailFrom(email_address_id='6467', name='Hayden Barnes')
    email = clicksend_client.Email(to=[defendant_email],
                                   bcc=[email_recipient],  # send to storage e-mail account for arching
                                   _from=[email_from],
                                   subject="Legal Advertising: Lawsuit Filed In Muscogee County",
                                   body="Court records show that a lawsuit was filed against [defendant_name] in Muscogee County, Georgia by [plaintiff_name_normalized] on [date_filed].\nIf you are the {{defendant_name_normalized}} named in this lawsuit and you are struggling to pay your bills we are here to help. We are bankruptcy lawyers dedicated to helping individuals and families experiencing temporary hardship regain their financial independence.\nAnyone can experience financial difficulties. Bankruptcy is designed to give those individuals and families a fresh start. Rather than waiting and worrying you can take your first steps to your financial freedom today.\nYou may be eligible to consolidate your debts into one lower monthly payment through a Chapter 13 reorganization. You may also be eligible to discharge your debts with a Chapter 7 bankruptcy. Both methods will stop creditors from calling, garnishing your wages, or taking your property.\nWe provide a free, no-obligation consultation to discuss your financial situation and whether bankruptcy is an option for you. Call us at 706.690.4471 day or night so we can schedule an appointment for you.")
    try:
        api_response = api_instance.email_send_post(email)
        print(api_response)
        # ! record clicksend api response to clicksend.log
    except ApiException as e:
        print("Exception when calling TransactionalEmailApi->email_send_post: %s\n" % e)

        return 0


def api_facebook(court_name, case_number, date_filed, plaintiff_name, defendant_name, defendant_facebook):
    # https://fbchat.readthedocs.io/en/latest/intro.html

    # TODO: Find a way to send a message from a Page not just a user using fbchat or other library.

    # adapted from sample code:

    from fbchat import Client
    import fbchat.models
    from api_keys import facebook_email, facebook_password

    client = Client(facebook_email, facebook_password)
    client.send(fbchat.models.Message(text="Message"), thread_id=client.uid,
                thread_type=fbchat.models.ThreadType.USER)
    # ! record facebook response to facebook.log

    return 0

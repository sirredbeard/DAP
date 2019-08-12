from piplapis.data import Person, Name, Address


def address_match(tree, address):
    """
    Checks if supplied address matches comparison tree, with the tree set-up according to:

    n = even --> tree[n]     = address dict key
                 tree[n + 1] = comparison value to compare to address dict key

    (please note: Address is a class object but we're reading the value directly with
                  address.__dict__[key] due to the way that python classes are setup)
    """
    length = len(tree)

    # Check we have a valid compare tree
    if not tree or length % 2 != 0:
        raise ValueError("Invalid compare tree!")

    index = 0
    while index < length:
        key = tree[index]
        comp_val = tree[index+1]

        # If the address object doesn't have a value for the required key,
        # or the corresponding value is different, return False
        if not address.__dict__[key] or address.__dict__[key] != comp_val:
            return False

        # step 2 along to the next key in compare tree
        index += 2

    return True


def get_matching_addresses(addresses = list(), house = "", apt = "", street = "", city = "", state = "", zip = "", type = ""):
    """
    For a supplied list of Address objects, returns only those that match
    all of the supplied (non-empty) address attributes
    """
    matching_addrs = list()

    # return if nothing to iterate
    if len(addresses) == 0: return matching_addrs

    # create comparison tree for looking at address attributes
    # (comparison tree is probably a really bad name for what this is
    #   but i can't think of another way to explain it :P)
    compare_tree = list()
    if house != "":
        compare_tree.append("house")
        compare_tree.append(house)
    if street != "":
        compare_tree.append("street")
        compare_tree.append(street)
    if apt != "":
        compare_tree.append("apt")
        compare_tree.append(apt)
    if city != "":
        compare_tree.append("city")
        compare_tree.append(city)
    if state != "":
        compare_tree.append("state")
        compare_tree.append(state)
    if zip != "":
        compare_tree.append("zip")
        compare_tree.append(zip)
    if type != "":
        compare_tree.append("type")
        compare_tree.append(type)

    # Compare each of the supplied addresses with the comparison tree
    for address in addresses:
        if address_match(compare_tree, address):
            matching_addrs.append(address)

    return matching_addrs

"""TODO:argparse options' help"""

import argparse
import json
from pathlib import Path
import re



"""Globals"""
ARGS = None
CONTACTS = {
    # "name"    :   "",
    # "phone"   :   ""
}

"""Error handler decorator"""
def error_handler(function):

    def wrapper(*args,**kwargs) -> str:
        result = ""
        try:
            result = function(*args,**kwargs)
        except KeyError as e:
            result = "Record with name=" + str(e) + " not found."
        except TypeError as e:
            result = e
        except Exception as e:
            result = e
        return result
    
    return wrapper

@error_handler
def load(args)-> str:
    db_file = None
    if args.file:
        db_file = args.file
    elif ARGS.db:
        db_file = ARGS.db
    if db_file and db_file.exists():
        with open(db_file, "r+") as db:
            contacts = json.load(db)
            if contacts:
                CONTACTS.update(contacts)
        return ""
    else:
        raise Exception(f"{db_file} not found.")

@error_handler
def save(args)-> str:
    db_file = None
    if args.file:
        db_file = args.file
    elif ARGS.db:
        db_file = ARGS.db
    if db_file:
        with open(db_file, "w+") as db:
            data = json.dumps(CONTACTS)
            db.write(data)
        return ""
    else:
        raise Exception("File name isn't specified.")


def hello(args)-> str:
    return "How can I help you?"


def bye(args)-> str:
    return "Good bye!"


"""TODO: use regexp"""
def check_phone(phone):
    if not phone.isdigit():
        raise TypeError(f"Phone:{phone} is not valid.")
    return phone


"""DB functions"""
@error_handler
def insert(args)-> str:
    phone = check_phone(args.phone)
    if CONTACTS.get(args.name):
        contact = {args.name:phone}
        raise Exception(f"Contact - {contact} already exist. Use update command instead.")
    CONTACTS[args.name] = phone
    # phone = CONTACTS[args.name]
    # if not phone:
    #     phone = check_phone(args.phone)
    #     CONTACTS[args.name] = phone
    #     return "" #f"Added contact - {contact}"
    # else:
    #     contact = {args.name:phone}
    #     return f"Contact - {contact} already exist. Use update command instead."
    return ""

@error_handler
def update(args)-> str:
    check_phone(args.phone)
    # contact = {args.name:CONTACTS[args.name]}
    # phone = CONTACTS[args.name]
    phone = CONTACTS[args.name]
    CONTACTS[args.name] = args.phone
    # contact_new = {args.name:CONTACTS[args.name]}
    return "" #f"Replaced contact - {contact} with {contact_new}"


@error_handler
def delete(args)-> str:
    phone = CONTACTS.pop(args.name)
    # if phone:
    #     # contact = {args.name:phone}
    #     return ""
    # else:
    #     return f"Contact {args.name} not found."


@error_handler
def delete_all(args)-> str:
    # global CONTACTS
    CONTACTS.clear()
    return "" #f"Removed all contacts"


@error_handler
def view(args)-> str:
    contact = {args.name:CONTACTS[args.name]}
    return f"{contact}"


@error_handler
def view_all(args)-> str:
    return f"{CONTACTS}"


def create_argument_parser():

    exit_alias = ["good","bye","good_bye","close"]
    exit_on_error = False

    """Global parser options"""
    parser = argparse.ArgumentParser(exit_on_error = exit_on_error)
    parser.add_argument(
        "--db",
        help="Specify path to DB(JSON) file. Ex: db.json",
        type = Path,
        metavar="db.json",
        default="db.json",
        required=False
    )

    """Internal parser options"""
    subparsers = parser.add_subparsers(dest="command")
    
    parser_insert = subparsers.add_parser("insert", exit_on_error = exit_on_error, aliases=["i","add","a"])
    parser_insert.add_argument("name")
    parser_insert.add_argument("phone")
    parser_insert.set_defaults(func=insert)

    parser_update = subparsers.add_parser("update", exit_on_error = exit_on_error, aliases=["u","change","c"])
    parser_update.add_argument("name")
    parser_update.add_argument("phone")
    parser_update.set_defaults(func=update)

    parser_delete = subparsers.add_parser("delete", exit_on_error = exit_on_error, aliases=["d","remove","r"])
    parser_delete.add_argument("name")
    parser_delete.set_defaults(func=delete)

    parser_delete_all = subparsers.add_parser("delete_all", exit_on_error=False, aliases=["da","clear"])
    parser_delete_all.set_defaults(func=delete_all)

    parser_view = subparsers.add_parser("view", exit_on_error = exit_on_error, aliases=["v","phone","p"])
    parser_view.add_argument("name")
    parser_view.set_defaults(func=view)

    parser_view_all = subparsers.add_parser("view_all", exit_on_error = exit_on_error, aliases=["va","show","show_all","sa"])
    parser_view_all.set_defaults(func=view_all)

    parser_hello = subparsers.add_parser("hello", exit_on_error=False, aliases=["h"])
    parser_hello.set_defaults(func=hello)

    parser_bye = subparsers.add_parser("exit", exit_on_error = exit_on_error, aliases=exit_alias)
    parser_bye.set_defaults(func=bye)

    parser_load = subparsers.add_parser("load", exit_on_error = exit_on_error, aliases=["l"])
    parser_load.add_argument("file",type=Path)
    parser_load.set_defaults(func=load)
    for action in parser_load._actions: # Hook for exit on exception - Positional options can't be unrequired
        action.required = False

    parser_save = subparsers.add_parser("save", exit_on_error = exit_on_error, aliases=["s"])
    parser_save.add_argument("file",type=Path)
    parser_save.set_defaults(func=save)
    for action in parser_save._actions: # Hook for exit on exception - Positional options can't be unrequired
        action.required = False

    return parser, exit_alias


def main():

    global CONTACTS
    global ARGS

    parser, exit_alias = create_argument_parser()
    ARGS = parser.parse_args()
    # Process options on load
    # load(ARGS.db)
    if ARGS.db.exists(): # Load DB
        with open(ARGS.db, "r+") as db:
            try:
                CONTACTS = json.load(db)
            except Exception as e:
                print("JSON file format error.")
     # Execute command
    if ARGS.command:
        result = ARGS.func(ARGS)
        if result: print(result)
        if ARGS.command in exit_alias:
            return

    while True:
        command = input(">")
        commands = re.split("\"|\'", command)
        if len(commands) == 1:
            commands = re.split(" ", command)
        commands = list(map(lambda x: x.strip(), commands))
        commands = list(filter(lambda x: len(x) ,commands))
        # Parse command
        try:
            parsed_commands = parser.parse_args(commands)
        except SystemExit as e: # Hook
            continue
        except argparse.ArgumentError as e:
            print(e)
            continue
        # Execute command
        result = parsed_commands.func(parsed_commands)
        if result: print(result)
        if parsed_commands.command in exit_alias:
            break
        continue


if __name__ == '__main__':
    main()
from collections import UserDict
from datetime import datetime, date, timedelta
import pickle

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            return str(e)
        except IndexError:
            return "Not enough arguments. Check command format."
        except KeyError or AttributeError:
            return "Contact not found."
    return inner


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    pass


class Phone(Field):
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Phone number must contain exactly 10 digits.")
        super().__init__(value)


class Birthday(Field):
    def __init__(self, value):
        try:
            datetime.strptime(value, "%d.%m.%Y")
            super().__init__(value)
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY.")


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def edit_phone(self, old_phone, new_phone):
        phone = self.find_phone(old_phone)
        if not phone:
            raise ValueError("Old phone not found.")
        phone.value = Phone(new_phone).value

    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
        return None

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        phones = ", ".join(p.value for p in self.phones)
        birthday = self.birthday.value if self.birthday else "not set"
        return f"{self.name.value}: phones [{phones}], birthday [{birthday}]"

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def get_upcoming_birthdays(self):
        today = date.today()
        result = []

        for record in self.data.values():
            if not record.birthday:
                continue

            birthday = datetime.strptime(record.birthday.value, "%d.%m.%Y").date()
            birthday_this_year = birthday.replace(year=today.year)

            if birthday_this_year < today:
                birthday_this_year = birthday.replace(year=today.year + 1)

            if 0 <= (birthday_this_year - today).days <= 7:
                congratulation_date = birthday_this_year

                if congratulation_date.weekday() == 5:
                    congratulation_date += timedelta(days=2)
                elif congratulation_date.weekday() == 6:
                    congratulation_date += timedelta(days=1)

                result.append({
                    "name": record.name.value,
                    "birthday": congratulation_date.strftime("%d.%m.%Y")
                })

        return result


@input_error
def parse_input(user_input):
    command, *args = user_input.strip().split()
    return command.lower(), args


@input_error
def add_contact(args, book):
    if len(args) < 2:
        raise ValueError("Usage: add [name] [phone]")
    name, phone = args[:2]

    record = book.find(name)
    if not record:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    else:
        message = "Contact updated."

    record.add_phone(phone)
    return message


@input_error
def change_contact(args, book):
    if len(args) < 3:
        raise ValueError("Usage: change [name] [old phone] [new phone]")
    name, old_phone, new_phone = args[:3]

    record = book.find(name)

    record.edit_phone(old_phone, new_phone)
    return "Phone number updated."


@input_error
def show_phone(args, book):
    if not args:
        raise ValueError("Usage: phone [name]")
    name = args[0]

    record = book.find(name)

    return ", ".join(p.value for p in record.phones)


@input_error
def show_all(args, book):
    if not book.data:
        return "Address book is empty."
    return "\n".join(str(record) for record in book.data.values())


@input_error
def add_birthday(args, book):
    if len(args) < 2:
        raise ValueError("Usage: add-birthday [name] [DD.MM.YYYY]")
    name, birthday = args[:2]

    record = book.find(name)

    record.add_birthday(birthday)
    return "Birthday added."


@input_error
def show_birthday(args, book):
    if not args:
        raise ValueError("Usage: show-birthday [name]")
    name = args[0]

    record = book.find(name)
    if not record or not record.birthday:
        raise KeyError

    return record.birthday.value


@input_error
def birthdays(args, book):
    upcoming = book.get_upcoming_birthdays()
    if not upcoming:
        return "No birthdays in the next 7 days."

    return "\n".join(
        f"{item['name']} → {item['birthday']}"
        for item in upcoming
    )

def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()

def main():
    
    book = load_data(filename="addressbook.pkl")
    print("Welcome to the assistant bot!")
    
    while True:
        try:
            user_input = input("Enter a command: ")
            command, args = parse_input(user_input)
            
            if command in ("close", "exit"):
                save_data(book, filename="addressbook.pkl")
                print("Good bye!")
                break

            elif command == "hello":
                print("How can I help you?")

            elif command == "add":
                print(add_contact(args, book))

            elif command == "change":
                print(change_contact(args, book))

            elif command == "phone":
                print(show_phone(args, book))

            elif command == "all":
                print(show_all(args, book))

            elif command == "add-birthday":
                print(add_birthday(args, book))

            elif command == "show-birthday":
                print(show_birthday(args, book))

            elif command == "birthdays":
                print(birthdays(args, book))

            else:
                print("Invalid command.")
        except ValueError:
            print("Write command in correct form.")


if __name__ == "__main__":
    main()
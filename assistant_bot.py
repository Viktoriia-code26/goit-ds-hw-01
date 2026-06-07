from collections import UserDict
from datetime import datetime, timedelta
import pickle

def input_error(func):
    def inner(args, *a, **kw):
        try:
            return func(args, *a, **kw)
        except ValueError as error:
            return str(error)
        except KeyError:
            return "Contact not found."
        except IndexError as error:
            return str(error) if str(error) else "Invalid input."
        except AttributeError:
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
            raise ValueError("Phone number must contain 10 digits.")
        
        super().__init__(value)

class Birthday(Field):
    def __init__(self, value):

        try:
         datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        
        super().__init__(value)

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None
    
    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                self.phones.remove(p)
                return
        
        raise ValueError(f"Phone {phone} not found.")
    
    def edit_phone(self, old_phone, new_phone):
        for index, p in enumerate(self.phones):
            if p.value == old_phone:
                self.phones[index] = Phone(new_phone)
                return
        
        raise ValueError(f"Phone {old_phone} not found.")
    
    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
        
        return None
    
    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)  
    
    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}, birthday: {self.birthday.value if self.birthday else 'Not specified'}"

class AddressBook(UserDict):

    def add_record(self, record: Record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)
    
    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def get_upcoming_birthdays(self):
        upcoming = []
        today = datetime.now().date()

        for record in self.data.values():
            if record.birthday:
                birthday = datetime.strptime(record.birthday.value, "%d.%m.%Y").date()
                birthday_this_year = birthday.replace(year=today.year)

                if birthday_this_year < today:
                    birthday_this_year = birthday_this_year.replace(year=today.year + 1)

                delta = (birthday_this_year - today).days

                if 0 <= delta <= 7:
                    congratulation_date = birthday_this_year

                    if congratulation_date.weekday() == 5:
                        congratulation_date += timedelta(days=2)
                    elif congratulation_date.weekday() == 6:
                        congratulation_date += timedelta(days=1)

                    upcoming.append({
                        "name": record.name.value,
                        "birthday": congratulation_date.strftime("%d.%m.%Y")
                    })

        return upcoming
    
    def __str__(self):
        return '\n'.join(str(record) for record in self.data.values())

@input_error
def add_birthday(args, book):
    name, birthday_str, *_ = args
    record = book.find(name)
    record.add_birthday(birthday_str)
    return "Birthday added."

@input_error
def show_birthday(args, book):
    name = args[0]
    record = book.find(name)

    if record.birthday is None:
        return "Birthday not found."

    return f"{record.name.value}'s birthday is {record.birthday.value}."

@input_error
def birthdays(args, book):
    upcoming = book.get_upcoming_birthdays()

    if not upcoming:
        return "No upcoming birthdays."

    return "\n".join(
        f"{item['name']}: {item['birthday']}"
        for item in upcoming
    )

@input_error
def add_contact(args, book: AddressBook):
    if len(args) < 2:
        raise IndexError("Give me name and phone please.")
    
    name, phone, *_ = args
    record = book.find(name)

    if record is None:
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
        raise IndexError("Give me name, old phone, and new phone please.")
    
    name, old_phone, new_phone, *_ = args
    record = book.find(name)  
    record.edit_phone(old_phone, new_phone)
    return "Contact updated."

@input_error
def show_phone(args, book):
    if len(args) < 1:
        raise IndexError("Give me name please.")
    name = args[0]
    record = book.find(name)
    return "; ".join(p.value for p in record.phones)

@input_error
def show_all(args, book):
    if not book.data:
        return "No contacts found."

    return str(book)


def parse_input(user_input):
    parts = user_input.split()
    if not parts:
        return "", []
    cmd = parts[0].lower()
    args = parts[1:]

    return cmd, args

def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()
    except  EOFError:
        return AddressBook()
    
def main():
    book = load_data()
    print("Welcome to the assistant bot!")

    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            save_data(book)
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


if __name__ == "__main__":
    main()
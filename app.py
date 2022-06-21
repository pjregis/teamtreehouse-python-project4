from models import Base, session, Product, engine
import csv
from datetime import datetime
import time
from decimal import Decimal, DecimalException


def menu():
    """
    Main menu for the application
    Returns menu choice from user
    """
    while True:
        print('''
          \rSTORE INVENTORY\n
          \rv) View a single product's inventory
          \ra) Add a new product to the database
          \rb) Make a backup of the entire inventory          
          \rq) Exit
          ''')
        choice = input('Choose an option: ').lower()
        if choice in ['v', 'a', 'b', 'q']:
            return choice
        else:
            input('Please choose a valid menu option. '
                  '\nPress enter to continue.')


def clean_id(id_str, options):
    try:
        product_id = int(id_str)
    except ValueError:
        input('''
              \n****** ID ERROR ******
              \rThe id should be a number.
              \rPress enter to try again.
              \r*************************''')
        return
    else:
        if product_id in options:
            return product_id
        else:
            input(f'''
              \n****** ID ERROR ******
              \rOptions: {options}
              \rPress enter to try again.
              \r*************************''')
            return


def clean_price(price):
    """
    Cleans the price string
    """
    try:
        if '$' in price:
            price_split = price.split('$')
            cleaned_price = Decimal(price_split[1])
        else:
            cleaned_price = Decimal(price)
    except (ValueError, DecimalException):
        input('''\n********** Price Error **********
              \rThe price should be a number without a currency symbol and not less than 0.
              \rExample: 10.99
              \rPress enter to try again.
              \r***********************************
              ''')
        return
    else:
        price_cents = (cleaned_price * 100)
        return int(price_cents)


def clean_quantity(quantity):
    """
    Cleans the quantity string
    """
    try:
        if quantity == '':
            raise ValueError
        cleaned_quantity = int(quantity)
        if cleaned_quantity < 0:
            raise ValueError
    except ValueError:
        input('''\n ********** Quantity Error **********
              \rThe quantity should be a whole number and not less than 0.
              \rExample: 13
              \rPress enter to try again.
              \r*************************************
              ''')
        return
    else:
        return cleaned_quantity


def add_csv():
    """
    Add products from csv to database
    if they aren't in the DB already
    """
    with open('inventory.csv') as csvfile:
        data = csv.DictReader(csvfile)
        for row in data:
            price = clean_price(row['product_price'])
            quantity = int(row['product_quantity'])
            updated = datetime.strptime(row['date_updated'], '%m/%d/%Y').date()
            product_in_db = session.query(Product).filter(Product.product_name == row['product_name']).one_or_none()
            if product_in_db == None:
                new_product = Product(product_name=row['product_name'], product_price=price,
                                      product_quantity=quantity, date_updated=updated)
                session.add(new_product)
            else:
                if product_in_db.date_updated > updated:
                    continue
                elif product_in_db.date_updated < updated:
                    product_in_db.product_price = price
                    product_in_db.product_quantity = quantity
                    product_in_db.date_updated = updated
                    continue
    session.commit()


def csv_backup():
    with open('backup.csv', 'w', newline='') as f:
        out = csv.writer(f)
        out.writerow(['product_name', 'product_price', 'product_quantity', 'date_updated'])

        for product in session.query(Product).all():
            out.writerow([product.product_name, f'${format(product.product_price / 100, ".2f")}',
                          product.product_quantity, product.date_updated.strftime("%m/%d/%Y")])


def app():
    """
    Main application function
    """
    app_running = True
    while app_running:
        choice = menu()
        if choice == 'v':
            id_options = []
            for product in session.query(Product):
                id_options.append(product.product_id)
            id_error = True
            while id_error:
                product_id = input(f'''\nOptions: {id_options}
                                    \rWhat is the product's id? ''')
                product_id = clean_id(product_id, id_options)
                if type(product_id) == int:
                    id_error = False
            the_product = session.query(Product).filter(Product.product_id == product_id).first()
            print(f'''\n**************************************************
                      \r{the_product.product_name}                  
                      \rPrice: ${format(the_product.product_price / 100, '.2f')}
                      \rQuantity: {the_product.product_quantity}
                      \rUpdated: {the_product.date_updated.strftime("%m/%d/%Y")}
                      \r**************************************************
                      ''')
            input('Press ENTER to continue.')
        elif choice == 'a':
            name_error = True
            price_error = True
            quantity_error = True
            print('\n*** Add a New Product ***')
            while name_error:
                name = input('Product Name: ')
                if len(name) <= 2:
                    print('Product names need to be at least 3 characters in length.')
                    input('Press ENTER to continue.')
                else:
                    name_error = False
            while price_error:
                price = input('Price (Example: 10.99): ')
                price = clean_price(price)
                if type(price) == int:
                    price_error = False
            while quantity_error:
                quantity = input('Quantity: ')
                quantity = clean_quantity(quantity)
                if type(quantity) == int:
                    quantity_error = False
            updated = datetime.now()
            product_in_db = session.query(Product).filter(Product.product_name == name).one_or_none()
            if product_in_db != None:
                product_in_db.product_price = price
                product_in_db.product_quantity = quantity
                product_in_db.date_updated = updated
                session.commit()
                print(f'\n"{product_in_db.product_name}" has been updated in the database successfully.')
            else:
                new_product = Product(product_name=name, product_price=price,
                                      product_quantity=quantity, date_updated=updated)
                session.add(new_product)
                session.commit()
                print(f'"{new_product.product_name}" has been added to the database successfully.')
            time.sleep(1.5)
        elif choice == 'b':
            csv_backup()
            print('The database has been backed up successfully.')
            time.sleep(1.5)
        elif choice == 'q':
            print('GOODBYE')
            app_running = False


if __name__ == '__main__':
    Base.metadata.create_all(engine)
    add_csv()
    app()

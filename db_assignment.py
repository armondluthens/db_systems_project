import mysql.connector
from mysql.connector import errorcode


class hotel_mgmt_control:

    def __init__(self):
        self.cnx = mysql.connector.connect(
            user='bpratherhuff', host='dbdev.divms.uiowa.edu', database='db_bpratherhuff', password='02btYCnf1=EY')
        self.curs = self.cnx.cursor()
        self.schema = []

    def read_schema(self):
        print("Reading schema from 'create-hotel.sql'")
        with open("create-hotel.sql") as f:
            lines = f.readlines()
            lines = [i.strip() for i in lines]
            lines = ' '.join(lines).split(';')
            lines = [i + ';' for i in lines]
            self.schema = lines[:-1]

    def create_tables(self):
        for t in self.schema:
            try:
                print("Creating table {}: ".format(name), end='')
                self.curs.execute(t)
            except mysql.connector.Error as err:
                if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                    print("already exists.")
                else:
                    print(err.msg)
            else:
                print("OK")


class hotel_mgmt_employee:

    def __init__(self, login_id=None):
        self.login_id = login_id

    def login(self):

    def rooms_occupied(self):

    def housekeeping(self):

    def check_in(self):

    def check_out(self):

    def mark_serviced(self):


class hotel_mgmt_customer:

    def __init__(self, login_id=None):
        self.login_id = login_id

    def login(self):

    def rooms_available(self):

    def cost_at_checkout(self):

    def my_reservations(self):

    def reserve(self):

    def cancel(self):

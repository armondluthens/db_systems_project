import mysql.connector
from mysql.connector import errorcode


class hotel_mgmt_control:

    def __init__(self):
        self.cnx = mysql.connector.connect(
            user='bpratherhuff', host='dbdev.divms.uiowa.edu', database='db_bpratherhuff', password='02btYCnf1=EY')
        self.schema = []

    def read_schema(self):
        """
        Read schema from 'create-hotel.sql'
        """
        print("Reading schema from 'create-hotel.sql'")
        with open("create-hotel.sql") as f:
            lines = f.readlines()
            lines = [i.strip() for i in lines]
            lines = ' '.join(lines).split(';')
            lines = [i + ';' for i in lines]
            self.schema = lines[:-1]

    def create_tables(self):
        """
        Create tables based on schema
        """
        curs = self.cnx.cursor()
        for t in self.schema:
            try:
                print("Creating table {}: ".format(name))
                curs.execute(t)
            except mysql.connector.Error as err:
                if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                    print("already exists.")
                else:
                    print(err.msg)
            else:
                print("OK")

    def close(self):
        """
        Clean up
        """
        self.cnx.close()


class hotel_mgmt_employee:

    def __init__(self, controller, login_id=None):
        self.login_id = login_id
        self.logged_in = False
        self.controller = controller

    def login(self):
        if login_id == None:
            self.logged_in = True
        else:
            try:
                controller.cnx.start_transaction()
                cur = controller.cnx.cursor()
                cur.execute("select * from Employee where employee_id = {};".format(self.login_id))
                res = cur.fetchall()
                if len(res) != 0:
                    self.logged_in = True
                else:
                    print("Manager Not Found. Creating New Manager.")
                    firstname = raw_input('Enter your first name: ')
                    lastname = raw_input('Enter your last name: ')
                    position = raw_input('Enter your position: ')
                    cur.execute("insert into Employee values ({},'{}','{}','{}');".format(self.login_id, firstname, lastname, position))

                    cur.execute("select * from Employee where cid = {};".format(self.login_id))
                    res = cur.fetchall()
                    if len(res) != 0:
                        self.logged_in = True
                self.cnx.commit()
                return res

            except mysql.connector.InternalError as e:
                print "failed to login: ", e
                try:
                    self.cnx.rollback()
                except mysql.connector.InternalError as e:
                    pass
                return None

    def rooms_occupied(self):
        if self.logged_in:
            try:
                controller.cnx.start_transaction()
                cur = controller.cnx.cursor()
                cur.execute("select * from Room where occupied_status = 1;")
                res = cur.fetchall()
                print("Rooms Occupied: ", res)
                self.cnx.commit()

            except mysql.connector.InternalError as e:
                print "failed to fetch rooms occupied: ", e
                try:
                    self.cnx.rollback()
                except mysql.connector.InternalError as e:
                    pass
                return None

    def housekeeping(self):
        if self.logged_in:
            try:
                controller.cnx.start_transaction()
                cur = controller.cnx.cursor()
                cur.execute("select * from House_Keeping;")
                res = cur.fetchall()
                print("Housekeeping Assignments: ", res)
                self.cnx.commit()

            except mysql.connector.InternalError as e:
                print "failed to fetch hosekeeping assignments: ", e
                try:
                    self.cnx.rollback()
                except mysql.connector.InternalError as e:
                    pass
                return None

    def check_in(self, customer_id, room_id):
        if self.logged_in:
            try:
                controller.cnx.start_transaction()
                cur = controller.cnx.cursor()
                cur.execute("select * from Reservation where cid = {} and room_id = {};".format(customer_id, room_id))
                res = cur.fetchall()
                if len(res) == 0:
                    print("Reservation Not Found")
                    return None
                else if len(res) > 1:
                    print("Multiple Reservations Found, Choose Index of Reservation")
                    for i in range(len(res)):
                        print(i,": ", res[i])
                    indx = raw_input("Index: ")
                    res = res[indx]
                else:
                    res = res[0]

                cur.execute("update Reservation set check_in_status = 1, check_in_date = NOW() where cid = {} and room_id = {} and reservation_date = '{}';".format(res[0], res[1], res[2]))

                print("Reservation Checked In: ", res)
                self.cnx.commit()
                return res

            except mysql.connector.InternalError as e:
                print "failed to check in: ", e
                try:
                    self.cnx.rollback()
                except mysql.connector.InternalError as e:
                    pass
                return None

    def check_out(self, customer_id, room_id):
        if self.logged_in:
            try:
                controller.cnx.start_transaction()
                cur = controller.cnx.cursor()
                cur.execute("select * from Reservation where cid = {} and room_id = {};".format(customer_id, room_id))
                res = cur.fetchall()
                if len(res) == 0:
                    print("Reservation Not Found")
                    return None
                else if len(res) > 1:
                    print("Multiple Reservations Found, Choose Index of Reservation.")
                    for i in range(len(res)):
                        print(i,": ", res[i])
                    indx = raw_input("Index: ")
                    res = res[indx]
                else:
                    res = res[0]

                cur.execute("update Reservation set check_out_status = 1, check_out_date = NOW() where cid = {} and room_id = {} and reservation_date = '{}';".format(res[0], res[1], res[2]))

                print("Reservation Checked Out: ", res)
                self.cnx.commit()
                return res

            except mysql.connector.InternalError as e:
                print "failed to check out: ", e
                try:
                    self.cnx.rollback()
                except mysql.connector.InternalError as e:
                    pass
                return None

    def mark_serviced(self, room, assigned_id, discript):
        if self.logged_in:
            try:
                controller.cnx.start_transaction()
                cur = controller.cnx.cursor()
                cur.execute("select * from House_Keeping where room_id = {} and assigned_to_id = {} and completion_status = 0;".format(room, assigned_id))
                res = cur.fetchall()

                if len(res) == 0:
                    print("No Assignments Found")
                    return None
                if len(res) > 1:
                    print("Multiple Assignments found, select index.")
                    for i in range(len(res)):
                        print(i,": ", res[i])
                    indx = raw_input("Index: ")
                    res = res[indx]
                else:
                    res = res[0]

                cur.execute("update House_Keeping set completion_status = 1, description = '{}' where room_id = {} and date_of_service = {};".format(discript, res[0], res[1]))

                print("Set Serviced: ", res)
                self.cnx.commit()
                return res

            except mysql.connector.InternalError as e:
                print "failed to check out: ", e
                try:
                    self.cnx.rollback()
                except mysql.connector.InternalError as e:
                    pass
                return None



class hotel_mgmt_customer:

    def __init__(self, controller, login_id=None):
        self.login_id = login_id
        self.logged_in = False
        self.controller = controller

    def login(self):
        if login_id == None:
            raise ValueError("Customer ID can't be empty!")
        else:
            try:
                controller.cnx.start_transaction()
                cur = controller.cnx.cursor()
                cur.execute("select * from Customer where cid = {};".format(self.login_id))
                res = cur.fetchall()
                if len(res) != 0:
                    self.logged_in = True
                else:
                    print("Customer Not Found. Creating New Customer.")
                    firstname = raw_input('Enter your first name: ')
                    lastname = raw_input('Enter your last name: ')
                    phone = raw_input('Enter your phone: ')
                    cur.execute("insert into Customer values ({},'{}','{}','{}');".format(self.login_id, firstname, lastname, phone))

                    cur.execute("select * from Customer where cid = {};".format(self.login_id))
                    res = cur.fetchall()
                    if len(res) != 0:
                        self.logged_in = True
                self.cnx.commit()
                return res

            except mysql.connector.InternalError as e:
                print "failed to login: ", e
                try:
                    self.cnx.rollback()
                except mysql.connector.InternalError as e:
                    pass
                return None

    def rooms_available(self):
    #SELECT * FROM Room WHERE occupied_status=0

    def cost_at_checkout(self):

    def my_reservations(self):
    #SELECT * FROM Reservation WHERE 

    def reserve(self):

    def cancel(self):

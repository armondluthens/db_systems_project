import mysql.connector
from mysql.connector import errorcode
import datetime


class hotel_mgmt_control:

    def __init__(self):
        self.cnx = mysql.connector.connect(
            user='bpratherhuff', host='dbdev.divms.uiowa.edu', database='db_bpratherhuff', password='02btYCnf1=EY')
        self.schema = []

        self.read_schema()
        self.create_tables()
        self.input_dummy_data()

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
                print("Creating tables")
                curs.execute(t)
            except mysql.connector.Error as err:
                if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                    print("already exists.")
                else:
                    print(err.msg)
            else:
                print("OK")

    def __repsint__(self, s):
        try:
            int(s)
            return True
        except ValueError:
            return False


    def input_dummy_data(self):
        curs = self.cnx.cursor()
        lines = []
        table = ""
        with open("dummy_data.csv", "r") as f:
            lines = f.readlines()
        lines = [l.strip() for l in lines]
        for l in lines:
            if l[0] == "/":
                table = l[2:]
            if self.__repsint__(l[0]):
                curs.execute("insert into {} values ({});".format(table, l))


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

        self.login()

    def login(self):
        if self.login_id == None:
            self.logged_in = True
        else:
            try:
                self.controller.cnx.start_transaction()
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
                self.controller.cnx.start_transaction()
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
                self.controller.cnx.start_transaction()
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
                self.controller.cnx.start_transaction()
                cur = controller.cnx.cursor()
                cur.execute("select * from Reservation where cid = {} and room_id = {};".format(customer_id, room_id))
                res = cur.fetchall()
                if len(res) == 0:
                    print("Reservation Not Found")
                    return None
                elif len(res) > 1:
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
                self.controller.cnx.start_transaction()
                cur = controller.cnx.cursor()
                cur.execute("select * from Reservation where cid = {} and room_id = {};".format(customer_id, room_id))
                res = cur.fetchall()
                if len(res) == 0:
                    print("Reservation Not Found")
                    return None
                elif len(res) > 1:
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
                self.controller.cnx.start_transaction()
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

        self.login()

    def login(self):
        if login_id == None:
            raise ValueError("Customer ID can't be empty!")
        else:
            try:
                self.controller.cnx.start_transaction()
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

        if self.logged_in:
            try:
                self.controller.cnx.start_transaction()
                cur = controller.cnx.cursor()
                cur.execute("select * from Rooms where occupied_status = 0 group by room_type;")
                res = cur.fetchall()
                rooms = []

                if len(res) > 0:
                    for r in res:
                        cur.execute("select * from Room_Type where room_type = {};".format(r[2]))
                        roomtype = cur.fetchall()
                        print(roomtype)
                        rooms.append(roomtype)
                else:
                    print("No Rooms Found")
                    return None

                self.cnx.commit()
                return rooms

            except mysql.connector.InternalError as e:
                print "failed to get avaliable rooms: ", e
                try:
                    self.cnx.rollback()
                except mysql.connector.InternalError as e:
                    pass
                return None


    def cost_at_checkout(self):
        #def cost_at_checkout(self):
        # tran_id = "SELECT transaction_id, DATE_DIFF(check_out_date, NOW()), as    num_days_early, room_id FROM Reservation where cid=? and room_id=? and reservation_date=?"
        # if(num_days_early > 0){
        #   rType = SELECT room_type FROM Room where room_type= "type returned from previous query"
        #   dailyCost = SELECT cost FROM Room_Type WHERE room_type = "room_type from previous query"
        #   refundAmount = dailyCost*numDaysEarly
        #   update refund days in transaction table
        # }
        # SELECT * from Transaction WHERE transaction_id="tran_id"

        if self.logged_in:
            try:
                self.controller.cnx.start_transaction()
                cur = controller.cnx.cursor()
                cur.execute("select * from Reservation where cid = {};".format(self.login_id))
                res = cur.fetchall()
                if len(res) == 0:
                    print("Reservation Not Found")
                    return None
                elif len(res) > 1:
                    print("Multiple Reservations Found, Choose Index of Reservation")
                    for i in range(len(res)):
                        print(i,": ", res[i])
                    indx = raw_input("Index: ")
                    res = res[indx]
                else:
                    res = res[0]

                f = '%Y-%m-%d %H:%M:%S'
                checkintime = datetime.datetime.strptime(res[3], f)
                checkouttime = datetime.datetime.strptime(res[4], f)

                delta = checkouttime - checkintime

                cur.execute("select * from Room where room_id = {};".format(res[1]))
                room = cur.fetchall()
                if len(room) != 1:
                    print("Room not found")
                    return None

                cur.execute("select cost from Room_Type where room_type = {};".format(room[0][2]))
                cost = cur.fetchall()
                if len(cost) != 1:
                    print("Cost not found")
                    return None
                else:
                    price = cost[0][0] * delta.days
                    print("Reservation will cost: {} at ${} per day for {} days.".format(price, cost[0][0], delta.days))

                self.cnx.commit()
                return price

            except mysql.connector.InternalError as e:
                print "failed to calculate cost: ", e
                try:
                    self.cnx.rollback()
                except mysql.connector.InternalError as e:
                    pass
                return None

    def my_reservations(self):
        if self.logged_in:
            try:
                self.controller.cnx.start_transaction()
                cur = controller.cnx.cursor()
                cur.execute("select * from Reservation where cid = {};".format(self.login_id))
                res = cur.fetchall()

                if len(res) > 0:
                    print(res)
                else:
                    print("No Reservations Found")
                    return None

                self.cnx.commit()
                return res

            except mysql.connector.InternalError as e:
                print "failed to find reservations: ", e
                try:
                    self.cnx.rollback()
                except mysql.connector.InternalError as e:
                    pass
                return None



    def reserve(self):
        if self.logged_in:
            try:
                self.controller.cnx.start_transaction()
                cur = controller.cnx.cursor()

                check_in_date = raw_input("Please select check in date (%Y-%m-%d): ")
                check_out_date = raw_input("Please select check out date (%Y-%m-%d): ")

                cur.execute("select distinct(room_type) from Room where occupied_status=0;")
                typesaval = cur.fetchall()
                print("Types avaliable:")
                for i in typesaval:
                    cur.execute("select * from Room_Type where room_type = {};".format(i))
                    print(i, ": ", cur.fetchall())
                r = raw_input("Select index of preferred room type.")

                rid = None
                for i in typesaval:
                    if int(r) == i[2]:
                        rid = i[0]
                        break

                cur.execute("insert into Reservation values ({}, {}, NOW(), '{}', '{}', 0,0,0);".format(self.login_id, rid, check_in_date, check_out_date))
                print("Room Reserved")
                self.cnx.commit()
                return "Success"

            except mysql.connector.InternalError as e:
                print "failed to find reservations: ", e
                try:
                    self.cnx.rollback()
                except mysql.connector.InternalError as e:
                    pass
                return None

    def cancel(self):
        if self.logged_in:
            try:
                self.controller.cnx.start_transaction()
                cur = controller.cnx.cursor()
                cur.execute("select * from Reservation where cid = {};".format(self.login_id))
                res = cur.fetchall()

                if len(res) > 0:
                    for i in range(len(res)):
                        print(i, ": ", res[i])
                    d = raw_input("Select the index of the reservation you wish to delete: ")
                    cur.execute("delete * from Reservation where cid = {} and room_id = {} and reservation_date = {};".format(res[int(d)][0], res[int(d)][1], res[int(d)][2]))
                    return res[d]
                else:
                    print("No Reservations Found")
                    return None

                self.cnx.commit()
                return res

            except mysql.connector.InternalError as e:
                print "failed to cancle reservation: ", e
                try:
                    self.cnx.rollback()
                except mysql.connector.InternalError as e:
                    pass
                return None

if __name__ == '__main__':
    ctrl = hotel_mgmt_control()
    mgr = hotel_mgmt_employee(ctrl)
    cust = hotel_mgmt_customer(ctrl,1)

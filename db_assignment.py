import mysql.connector
from mysql.connector import errorcode
import datetime

from multiprocessing import Process
import sys


class hotel_mgmt_control:
    '''
    Creating database connection.
    '''
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

    '''
    reading in and populating tables with
    dummy data csv file
    '''
    def input_dummy_data(self):
        curs = self.cnx.cursor()
        lines = []
        table = ""
        with open("dummy-data.csv", "r") as f:
            lines = f.readlines()
        lines = [l.strip() for l in lines]
        for l in lines:
            if l != "":
                if l[0] == "/":
                    table = l[2:]
                if self.__repsint__(l[0]):
                    try:
                        curs.execute("insert into {} values ({});".format(table, l))
                    except:
                        print "entry exists"
        self.cnx.commit()


    def close(self):
        """
        Clean up
        """
        self.cnx.close()

'''
This class incorporates all functionality for the database
from the hotel management side. The hotel management can
update reservations, and control room servicing assignments.
'''
class hotel_mgmt_employee:

    def __init__(self, controller, login_id=None):
        self.login_id = login_id
        self.logged_in = False
        self.controller = controller

        self.login()

    '''
    Hotel customer side function to log a hotel employee
    into their account
    '''
    def login(self):
        if self.login_id == None:
            self.logged_in = True
        else:
            try:
                self.controller.cnx.start_transaction()
                cur = self.controller.cnx.cursor()
                cur.execute("select * from Employee where employee_id={};".format(self.login_id))
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
                self.controller.cnx.commit()
                return res

            except mysql.connector.InternalError as e:
                print "failed to login: ", e
                try:
                    self.controller.cnx.rollback()
                except mysql.connector.InternalError as e:
                    pass
                return None

    '''
    Hotel management side function to query
    for all rooms that are currently occupied.
    Must be logged in to execute the query. If
    query fails, a failure message occurs and
    a rollback occurs.
    '''
    def rooms_occupied(self):
        if self.logged_in:
            try:
                self.controller.cnx.start_transaction()
                cur = self.controller.cnx.cursor()
                cur.execute("select * from Room where occupied_status = 1;")
                res = cur.fetchall()

                for t in res:
                    print ("room occupied: ", t[0])
                print("\n")

                self.controller.cnx.commit()
                return res

            except mysql.connector.InternalError as e:
                print "failed to fetch rooms occupied: ", e
                try:
                    self.controller.cnx.rollback()
                except mysql.connector.InternalError as e:
                    pass
                return None

    '''
    Hotel management side function to query
    for for all housekeeping assignments.
    Must be logged in to execute the query. If
    query fails, a failure message occurs and
    a rollback occurs.
    '''
    def housekeeping(self):
        if self.logged_in:
            try:
                self.controller.cnx.start_transaction()
                cur = self.controller.cnx.cursor()
                cur.execute("select * from House_Keeping;")
                res = cur.fetchall()
                #print("Housekeeping Assignments: ", res)
                print("\nHousekeeping Assignments:")
                for t in res:
                    print("assignment: " + str(t))
                print("\n")

                self.controller.cnx.commit()
                return res

            except mysql.connector.InternalError as e:
                print "failed to fetch hosekeeping assignments: ", e
                try:
                    self.controller.cnx.rollback()
                except mysql.connector.InternalError as e:
                    pass
                return None

    '''
    Hotel management side function to query
    to check a guest in to their room.  The query will
    return all reservations found for a customer id  and
    room id. After the checkin is completed, the reservation
    checked in status will be updated from false to true.
    Must be logged in to execute the query. If
    query fails, a failure message occurs and
    a rollback occurs.
    '''
    def check_in(self, customer_id, room_id):
        if self.logged_in:
            try:
                self.controller.cnx.start_transaction()
                cur = self.controller.cnx.cursor()
                cur.execute("select * from Reservation where cid = {} and room_id = {};".format(customer_id, room_id))
                res = cur.fetchall()
                if len(res) == 0:
                    print("Reservation Not Found")
                    self.controller.cnx.commit()
                    return None
                elif len(res) > 1:
                    print("Multiple Reservations Found, Choose Index of Reservation")
                    for i in range(len(res)):
                        print(str(i) + ": " + str(res[i]))
                    indx = int(raw_input("Index: "))
                    res = res[indx]
                else:
                    res = res[0]

                # check if reservation is allowed to be checked in today
                if res[3].date() != datetime.datetime.today().date():
                        raise mysql.connector.InternalError("Can't check in today!")

                cur.execute("update Reservation set checked_in_status=1, check_in_date = NOW() where cid = {} and room_id = {} and reservation_date = '{}';".format(res[0], res[1], res[2]))

                print("\nReservation Checked In: " + str(res) + "\n")

                self.controller.cnx.commit()
                return res

            except mysql.connector.InternalError as e:
                print "failed to check in: ", e
                try:
                    self.controller.cnx.rollback()
                except mysql.connector.InternalError as e:
                    pass
                return None

    '''
    Hotel management side function to query
    to check a guest out of their room.  The query will
    return all reservations found for a customer id  and
    room id. After the checkin is completed, the reservation
    checked out status will be updated from false to true.
    Must be logged in to execute the query. If
    query fails, a failure message occurs and
    a rollback occurs.
    '''
    def check_out(self, customer_id, room_id):
        if self.logged_in:
            try:
                self.controller.cnx.start_transaction()
                cur = self.controller.cnx.cursor()
                cur.execute("select * from Reservation where cid = {} and room_id = {};".format(customer_id, room_id))
                res = cur.fetchall()
                if len(res) == 0:
                    print("Reservation Not Found")
                    self.controller.cnx.commit()
                    return None
                elif len(res) > 1:
                    print("Multiple Reservations Found, Choose Index of Reservation.")
                    for i in range(len(res)):
                        print(str(i) + ": " + str(res[i]))
                    indx = int(raw_input("\nIndex: "))

                    res = res[indx]

                else:
                    res = res[0]

                #check if need refund
                if res[4].date() < datetime.datetime.today().date():
                    cur.execute('select * from Room where room_id={};'.format(res[1]))
                    room = cur.fetchall()[0]
                    cur.execute('select cost from Room_Type where room_type={};'.format(room[2]))
                    cost = cur.fetchall()[0]
                    refund = (res[4].day - res[3].day) * cost
                    print("Refund is: {}".format(refund))

                cur.execute("update Reservation set checked_out_status=1, check_out_date = NOW() where cid = {} and room_id = {} and reservation_date = '{}';".format(res[0], res[1], res[2]))

                print("Reservation Checked Out: " + str(res) + "\n")

                self.controller.cnx.commit()
                return res

            except mysql.connector.InternalError as e:
                print "failed to check out: ", e
                try:
                    self.controller.cnx.rollback()
                except mysql.connector.InternalError as e:
                    pass
                return None

    '''
    Hotel management side function to query
    for a room service assignment. Once the room has
    been serviced, the completion status of the room
    service assignment is updated from false to true.
    Must be logged in to execute the query. If
    query fails, a failure message occurs and
    a rollback occurs.
    '''
    def mark_serviced(self, room, assigned_id, discript):
        if self.logged_in:
            try:
                self.controller.cnx.start_transaction()
                cur = self.controller.cnx.cursor()
                cur.execute("select * from House_Keeping where room_id = {} and assigned_to_id = {} and completion_status = 0;".format(room, assigned_id))
                res = cur.fetchall()

                if len(res) == 0:
                    print("No Assignments Found")
                    self.controller.cnx.commit()
                    return None
                if len(res) > 1:
                    print("Multiple Assignments found, select index.")
                    for i in range(len(res)):
                        print(i,": ", res[i])
                    indx = int(raw_input("Index: "))
                    res = res[indx]
                else:
                    res = res[0]

                if res[5] != 0:
                    raise mysql.connector.InternalError('Room already serviced')

                cur.execute("update House_Keeping set completion_status=1, description='{}' where room_id={} and date_of_service='{}';".format(discript, res[0], res[1]))

                print("Set Serviced: " + str(room) + str(assigned_id))
                print("\n")
                for t in res:
                    print("Reservation: " + str(t))

                self.controller.cnx.commit()
                return res

            except mysql.connector.InternalError as e:
                print "failed to mark serviced: ", e
                try:
                    self.controller.cnx.rollback()
                except mysql.connector.InternalError as e:
                    pass
                return None


'''
This class incorporates all functionality for the database
from the hotel customer side. Hotel customers can view
reservations, check room availability for booking, and
view costs.
'''
class hotel_mgmt_customer:

    '''
    Hotel customer side function to create a customer object.
    This will give the customer its necessary attributes
    for querying within the  application. If query fails, a
    failure message occurs and a rollback occurs.
    '''
    def __init__(self, controller, login_id=None):
        self.login_id = login_id
        self.logged_in = False
        self.controller = controller

        self.login()

    '''
    Hotel customer side function to log a customer into
    their account
    '''
    def login(self):
        if self.login_id == None:
            raise ValueError("Customer ID can't be empty!")
        else:
            try:
                self.controller.cnx.start_transaction()
                cur = self.controller.cnx.cursor()
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
                self.controller.cnx.commit()
                return res

            except mysql.connector.InternalError as e:
                print "failed to login: ", e
                try:
                    self.controller.cnx.rollback()
                except mysql.connector.InternalError as e:
                    pass
                return None

    '''
    Hotel customer side function to query
    for all rooms that are currently available.
    Must be logged in to execute the query. If
    query fails, a failure message occurs and
    a rollback occurs.
    '''
    def rooms_available(self):

        if self.logged_in:
            try:
                self.controller.cnx.start_transaction()
                cur = self.controller.cnx.cursor()
                cur.execute("select * from Room where occupied_status = 0 group by room_type;")
                res = cur.fetchall()
                rooms = []

                if len(res) > 0:
                    for r in res:
                        cur.execute("select * from Room_Type where room_type = {};".format(r[2]))
                        roomtype = cur.fetchall()
                        #print(roomtype)
                        print("Room:")
                        for t in roomtype:
                            print t
                        rooms.append(roomtype)
                else:
                    print("No Rooms Found")
                    return None

                self.controller.cnx.commit()
                return rooms

            except mysql.connector.InternalError as e:
                print "failed to get avaliable rooms: ", e
                try:
                    self.controller.cnx.rollback()
                except mysql.connector.InternalError as e:
                    pass
                return None

    '''
    Hotel customer side function to query
    for  their cost at checkout.  If the checkout date is
    earlier than the expected checkout date, a refund is
    calcuated and deducted from the original cost.
    Must be logged in to execute the query. If query fails,
    a failure message occurs and a rollback occurs.
    '''
    def cost_at_checkout(self):

        if self.logged_in:
            try:
                self.controller.cnx.start_transaction()
                cur = self.controller.cnx.cursor()
                cur.execute("select * from Reservation where cid = {};".format(self.login_id))
                res = cur.fetchall()
                if len(res) == 0:
                    print("Reservation Not Found")
                    return None
                elif len(res) > 1:
                    print("\nMultiple Reservations Found, Choose Index of Reservation")
                    for i in range(len(res)):
                        print(str(i) + ": " + str(res[i]))
                    indx = int(raw_input("Index: "))
                    res = res[indx]
                else:
                    res = res[0]

                f = '%Y-%m-%d %H:%M:%S'
                checkintime = res[3]
                checkouttime = res[4]

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
                    print("\n")

                self.controller.cnx.commit()
                return price

            except mysql.connector.InternalError as e:
                print "failed to calculate cost: ", e
                try:
                    self.controller.cnx.rollback()
                except mysql.connector.InternalError as e:
                    pass
                return None

    '''
    Hotel customer side function to query
    for  the details of their reservation.
    Must be logged in to execute the query. If query fails,
    a failure message occurs and a rollback occurs.
    '''
    def my_reservations(self):
        if self.logged_in:
            try:
                self.controller.cnx.start_transaction()
                cur = self.controller.cnx.cursor()
                cur.execute("select * from Reservation where cid = {};".format(self.login_id))
                res = cur.fetchall()

                if len(res) > 0:
                    #print(res)
                    for tuple in res:
                        print tuple
                else:
                    print("No Reservations Found")
                    return None

                self.controller.cnx.commit()
                return res

            except mysql.connector.InternalError as e:
                print "failed to find reservations: ", e
                try:
                    self.controller.cnx.rollback()
                except mysql.connector.InternalError as e:
                    pass
                return None


    '''
    Hotel customer side function to create a reservation.
    Must be logged in to execute the query. If query fails,
    a failure message occurs and a rollback occurs.
    '''
    def reserve(self):
        if self.logged_in:
            try:
                self.controller.cnx.start_transaction()
                cur = self.controller.cnx.cursor()

                check_in_date = raw_input("Please select check in date (YYYY-MM-DD): ")
                check_out_date = raw_input("Please select check out date (YYYY-MM-DD): ")

                cur.execute("select distinct(room_type) from Room where occupied_status=0;")
                typesaval = cur.fetchall()

                cur.execute("select * from Reservation where '{}' >= check_in_date and '{}' <= check_out_date;".format(check_in_date, check_in_date))
                reserved_rooms = cur.fetchall()

                print("Types avaliable:")
                for i in typesaval:
                    cur.execute("select * from Room_Type where room_type={};".format(i[0]))
                    print(str(i) + ": " + str(cur.fetchall()))
                room_type = int(raw_input("Select index of preferred room type: "))

                cur.execute("select room_type, room_id from Room where occupied_status=0;")
                rooms_aval = cur.fetchall()

                rid = None
                for i in rooms_aval:
                    if room_type == i[0] and i[1] not in [r[1] for r in reserved_rooms]:
                        rid = i[1]
                        break

                if rid == None:
                    raise mysql.connector.InternalError("No rooms of type avaliable on date")

                cur.execute("insert into Reservation values ({}, {}, NOW(), '{}', '{}', 0,0,0);".format(self.login_id, rid, check_in_date, check_out_date))
                self.controller.cnx.commit()
                print("({}, {}, '{}', '{}', 0,0,0)".format(self.login_id, rid, check_in_date, check_out_date))
                print("\nYou have successfully made a reservation.\n")
                return "({}, {}, '{}', '{}', 0,0,0)".format(self.login_id, rid, check_in_date, check_out_date)

            except mysql.connector.InternalError as e:
                print "failed to find reservations: ", e
                try:
                    self.controller.cnx.rollback()
                except mysql.connector.InternalError as e:
                    pass
                return None


    def reserve_test(self, check_in_date, check_out_date, room_type):
        if self.logged_in:
            try:
                self.controller.cnx.start_transaction()
                cur = self.controller.cnx.cursor()
                
                #check_in_date = raw_input("Please select check in date (YYYY-MM-DD): ")
                #check_out_date = raw_input("Please select check out date (YYYY-MM-DD): ")
            
                cur.execute("select distinct(room_type) from Room where occupied_status=0;")
                typesaval = cur.fetchall()
                
                cur.execute("select * from Reservation where '{}' >= check_in_date and '{}' <= check_out_date;".format(check_in_date, check_in_date))
                reserved_rooms = cur.fetchall()
                
                print("Types avaliable:")
                for i in typesaval:
                    cur.execute("select * from Room_Type where room_type={};".format(i[0]))
                    print(str(i) + ": " + str(cur.fetchall()))
                #room_type = int(raw_input("Select index of preferred room type: "))
                
                cur.execute("select room_type, room_id from Room where occupied_status=0;")
                rooms_aval = cur.fetchall()
                
                rid = None
                for i in rooms_aval:
                    if room_type == i[0] and i[1] not in [r[1] for r in reserved_rooms]:
                        rid = i[1]
                        break
    
                if rid == None:
                    raise mysql.connector.InternalError("No rooms of type avaliable on date")
                
                cur.execute("insert into Reservation values ({}, {}, NOW(), '{}', '{}', 0,0,0);".format(self.login_id, rid, check_in_date, check_out_date))
                self.controller.cnx.commit()
                print("({}, {}, '{}', '{}', 0,0,0)".format(self.login_id, rid, check_in_date, check_out_date))
                print("\nYou have successfully made a reservation.\n")
                return "({}, {}, '{}', '{}', 0,0,0)".format(self.login_id, rid, check_in_date, check_out_date)
            
            except mysql.connector.InternalError as e:
                print "failed to find reservations: ", e
                try:
                    self.controller.cnx.rollback()
                except mysql.connector.InternalError as e:
                    pass
                return None

    '''
    Hotel customer side function to cancel a reservation.
    Must be logged in to execute the query. If query fails,
    a failure message occurs and a rollback occurs.
    '''
    def cancel(self):
        if self.logged_in:
            try:
                self.controller.cnx.start_transaction()
                cur = self.controller.cnx.cursor()
                cur.execute("select * from Reservation where cid = {};".format(self.login_id))
                res = cur.fetchall()

                if len(res) > 0:
                    for i in range(len(res)):
                        print(str(i) + ": " + str(res[i]))
                    d = raw_input("Select the index of the reservation you wish to delete: ")
                    if res[int(d)][4].date() == datetime.datetime.today().date():
                        raise mysql.connector.InternalError("Can't cancel on same day")
                    cur.execute("delete from Reservation where cid = {} and room_id = {} and reservation_date = '{}';".format(res[int(d)][0], res[int(d)][1], res[int(d)][2]))

                    print("\nSuccessful Cancelation.")
                    return res[int(d)]
                else:
                    print("No Reservations Found")
                    return None

                self.controller.cnx.commit()
                return res

            except mysql.connector.InternalError as e:
                print "failed to cancel reservation: ", e
                try:
                    self.controller.cnx.rollback()
                except mysql.connector.InternalError as e:
                    pass
                return None

    def cancel_test(self, d):
        if self.logged_in:
            try:
                self.controller.cnx.start_transaction()
                cur = self.controller.cnx.cursor()
                cur.execute("select * from Reservation where cid = {};".format(self.login_id))
                res = cur.fetchall()
            
                if len(res) > 0:
                    for i in range(len(res)):
                        print(str(i) + ": " + str(res[i]))
                #d = raw_input("Select the index of the reservation you wish to delete: ")
                    if res[int(d)][4].date() == datetime.datetime.today().date():
                        raise mysql.connector.InternalError("Can't cancel on same day")
                    cur.execute("delete from Reservation where cid = {} and room_id = {} and reservation_date = '{}';".format(res[int(d)][0], res[int(d)][1], res[int(d)][2]))
                    
                    print("\nSuccessful Cancelation.")
                    return res[int(d)]
                else:
                    print("No Reservations Found")
                    return None
    
                self.controller.cnx.commit()
                return res
            
            except mysql.connector.InternalError as e:
                print "failed to cancel reservation: ", e
                try:
                    self.controller.cnx.rollback()
                except mysql.connector.InternalError as e:
                    pass
                return None

'''
Program driver that creates objects for both classes
and calls hotel management functions, as well as the
functions for creating the tables and reading data
into them.
'''
if __name__ == '__main__':
    ctrl = hotel_mgmt_control()
    ctrl.read_schema()
    ctrl.create_tables()
    ctrl.input_dummy_data()

    print("\n")
    print("Controller Initialized")

    mgr = hotel_mgmt_employee(ctrl,1)
    print("Employee Initialized")
    print("\n")

    mgr.rooms_occupied()
    mgr.housekeeping()
    mgr.check_in(1,1)
    mgr.check_out(1,1)
    mgr.mark_serviced(5,5,"Cleaned the room")

    print("\n")
    print("Customer Initialized")
    cust = hotel_mgmt_customer(ctrl,1)
    print("Customer 2 Initialized")
    cust2 = hotel_mgmt_customer(ctrl,2)
    
    
    cust.rooms_available()
    
    cust.cost_at_checkout()
    cust.my_reservations()
    #cust.reserve()
    cust.cancel()
    
    

    ## Test Cases
    #trying to cancel on the same day test
    cust.cancel_test(1)
    
    #make reservation
    cust.reserve_test('2016-05-05', '2016-06-07', 1)
    
    #reserving a reservation thats already made should fail
    cust.reserve_test('2016-05-05', '2016-06-07', 1)

    #Two customers make the same reservation at the same time on different threads
    p1 = Process(target = cust.reserve_test('2016-07-07', '2016-07-011', 1))
    p1.start()
    p2 = Process(target = cust2.reserve_test('2016-07-07', '2016-07-011', 1))
    p2.start()


    #check in a member that is already checked in
    mgr.check_in(1,6)

    ## ## ## should pass
    mgr.check_in(1,7)

    ## ## Check out
    ## ## ## no refund
    mgr.check_out(1,6)
    ## ## ## should refund
    mgr.check_out(1,7)

















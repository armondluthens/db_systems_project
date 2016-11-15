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



#Required queries to support
#a. view the currently occupied rooms
#b. view the room types and costs that are still available
#c. calculate the total cost for a guest at checkout time
#d. list future reservations for a guest
#e. list house-keeping assignments

class hotel_mgmt_customer:

    def __init__(self, login_id=None):
        self.login_id = login_id

    def login(self):

    def rooms_available(self):
    # SELECT room_id FROM Room WHERE occupied_status='0';
    
    def cost_at_checkout(self):
    # tran_id = "SELECT transaction_id, DATE_DIFF(check_out_date, NOW()), as num_days_early, room_id FROM Reservation where cid=? and room_id=? and reservation_date=?"
    # if(num_days_early > 0){
    #   rType = SELECT room_type FROM Room where room_type= "type returned from previous query"
    #   dailyCost = SELECT cost FROM Room_Type WHERE room_type = "room_type from previous query"
    #   refundAmount = dailyCost*numDaysEarly
    #   update refund days in transaction table
    # }
    # SELECT * from Transaction WHERE transaction_id="tran_id"
    #

    def my_reservations(self):
    # SELECT * FROM Reservation where cid=? and room_id=? and reservation_date=?

    def reserve(self):

    def cancel(self):

/******************************************************************
    Armond Luthens & Bryan Prather-Huff
    CS4400: Database Systems Homework #6
    Group #2
    File Name: create-hotel.sql
    Instructor: Brandon Myers
    Due Date: Thursday, November 8, 2016 @ 11:59pm
*******************************************************************/

create table Customer (
   cid int PRIMARY KEY,
  first_name varchar(20),
  last_name varchar(20),
  phone varchar(10)
);

create table Room_Type (
  room_type int PRIMARY KEY,
  no_people int,
  cost int
);

create table Transaction (
  transaction_id int PRIMARY KEY,
  amount int,
  payment_method varchar(20),
  payment_date timestamp,
  refund_amount int
);

create table Employee (
  employee_id int PRIMARY KEY,
  first_name varchar(20),
  last_name varchar(20),
  position varchar(20)
);

create table Room (
  room_id int PRIMARY KEY,
  occupied_status boolean,
  room_type int REFERENCES Room_Type
);

create table Reservation (
  cid int REFERENCES Customer,
  room_id int REFERENCES Room,
  reservation_date timestamp,
  check_in_date timestamp,
  check_out_date timestamp,
  checked_in_status boolean,
  checked_out_status boolean,
  transaction_id int REFERENCES Transaction,
  PRIMARY KEY(cid, room_id, reservation_date)
);

create table House_Keeping (
  room_id int REFERENCES Room,
  date_of_service timestamp,
  assigned_by_id int REFERENCES Employee,
  assigned_to_id int REFERENCES Employee,
  description varchar(500),
  completion_status boolean,
  PRIMARY KEY(room_id, date_of_service)
);

/*
.mode csv
.import /home/.../file.csv <tablename>
*/

create table cust (
emailaddress string, 
firstname string,
lastname string,
address string,
address2 string,
city string,
state string,
zip string,
billingaddress string,
billingzip string,
notes string,
datecreated datetime,
birthdate date,
phone string,
phone2 string,
id int,
memberof string,
referrer string,
classcount int,
firstclass datetime,
lastclass datetime,
company string,
keytag string,
emergencycontact string,
emergencyphone string,
preferredlocation string,
gender string,
weight float,
primary key (id)
);

create table sale (
dt datetime,
custid int,
pmtype string,
total float,
item string,
typ string,
firstname string,
lastname string,
studio string,
id INTEGER PRIMARY KEY AUTOINCREMENT
);

create table attend (
id int,
custid int,
firstname string,
lastname string,
emailaddress string,
status string,
spot int,
datein datetime,
seriesid int,
series string,
classdate datetime,
classtype string,
inst string,
room string,
cost float,
primary key (id)
);


create view v_sale as select * from sale left join cust on sale.custid=cust.id;

-- get sales by city
select lower(city), sum(total) from v_sale group by lower(city) having sum(total)>0 order by sum(total) desc;

-- sales by city by month
select strftime('%Y-%m',dt) as yymm, lower(city) as cty, sum(total) as ttl 
from v_sale 
where cty in ('ridgefield','wilton') 
group by yymm, cty 
having ttl>0 
order by yymm,cty;

create view vw_birthday as select id, firstname, lastname, emailaddress, birthdate, strftime("%m-%d", birthdate) as mmdd from cust;

select * from vw_birthday where mmdd = '07-17';

-- super16 stuff
select firstname, lastname, count(*) 
from attend 
where status='Enrolled' and date(classdate) >= '2014-07-01' and date(classdate) <= '2014-07-22' 
group by firstname, lastname 
having count(*) > 5 
order by lastname, firstname;

-- 100 rider wall of joy stuff
select firstname, lastname, count(*) as cnt, date(classdate) as asof from attend 
group by firstname, lastname 
order by lastname, firstname;



-- attendance by customer by month
create view vw_attendbymonth as select custid, firstname, lastname, count(*) as cnt, strftime("%m-%Y", classdate) as mmyy from attend where status='Enrolled' group by custid, mmyy;

--note: we add 7 days here because the person might have future bookings; don't want to consider someone lapsed if they have lots of future bookings

drop view vw_attendlast30;
create view vw_attendlast30 as select custid, attend.firstname, attend.lastname, attend.emailaddress, 
phone, phone2, count(*) as cnt, date('now','-30 days') as start, 
date('now', '+7 days') as end 
from attend join cust on attend.custid=cust.id where status='Enrolled' and 
	classdate >=start and classdate <= end group by custid;

drop view vw_attendprev30;
create view vw_attendprev30 as select custid, a.firstname, a.lastname, a.emailaddress,
phone, phone2, count(*) as cnt, date('now','-60 days') as start, 
date('now', '-30 days') as end 
from attend a join cust c on a.custid=c.id where status='Enrolled' and 
classdate >=start and classdate < end group by custid;

drop view vw_riderstrendingup;
create view vw_riderstrendingup as 
select v1.custid, v1.firstname, v1.lastname, v1.emailaddress, v1.phone, v1.phone2, v1.cnt as prev30, v2.cnt as last30 
from vw_attendprev30 v1 left outer join vw_attendlast30 v2 on v1.custid=v2.custid 
where last30 > prev30 
order by last30-prev30 desc;

-- note: the complicated order by is designed to flag the best customers who are trending down
drop view vw_riderstrendingdown;
create view vw_riderstrendingdown as 
select v1.custid, v1.firstname, v1.lastname, v1.emailaddress, v1.phone, v1.phone2, 
v1.cnt as prev30, v2.cnt as last30 from vw_attendprev30 v1 left outer join vw_attendlast30 v2 on v1.custid=v2.custid 
where prev30 > 0 and prev30 > last30 
order by (1.0*prev30)/(1*last30) * (prev30-last30) desc;

drop view vw_riderslapsed;
create view vw_riderslapsed as 
select v1.custid, v1.firstname, v1.lastname, v1.emailaddress, v1.phone, v1.phone2,
v1.cnt as prev30 from vw_attendprev30 v1 left outer join vw_attendlast30 v2 on v1.custid=v2.custid 
where prev30 > 0 and v2.cnt is null 
order by prev30 desc;

-- list upcoming milestone riders (multiple of 50)
drop view vw_milestone;
create view vw_milestone as select custid, a.firstname, a.lastname, a.emailaddress, phone, phone2, 
count(*) as cnt, max(classdate) as classdate 
from attend a join cust c on a.custid=c.id 
where status='Enrolled' and date(classdate)<=date('now','+10 day') 
group by custid having cnt % 50 = 0;

select custid, firstname, lastname, count(*) as cnt, max(classdate) as maxclassdate from attend where status='Enrolled' and date(classdate)<=date('now','+20 days') group by custid;


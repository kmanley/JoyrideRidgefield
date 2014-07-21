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

create view vw_birthday as select firstname, lastname, emailaddress, birthdate, strftime("%m-%d", birthdate) as mmdd from cust;

select * from vw_birthday where mmdd = '07-17';

-- super16 stuff
select firstname, lastname, count(*) 
from attend 
where status='Enrolled' and date(classdate) >= '2014-07-01' and date(classdate) <= '2014-07-18' 
group by firstname, lastname 
having count(*) > 5 
order by lastname, firstname;







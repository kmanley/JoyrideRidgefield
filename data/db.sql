/*
.mode csv
.import /home/.../file.csv <tablename>
*/

/* TODO: NOTE: should be forcing localtime, currently getting UTC
select date('now', 'localtime', '-1 day');
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

create view vw_cust
as
select *, cast((julianday()-julianday(birthdate))/365.25 as int) as age
from cust;

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
datein datetime,b
seriesid int,
series string,
classdate datetime,
classtype string,
inst string,
room string,
cost float,
num int,
totnum int,
primary key (id)
);

create view v_sale as select * from sale left join cust on sale.custid=cust.id;

-- get sales by city
--select lower(city), sum(total) from v_sale group by lower(city) having sum(total)>0 order by sum(total) desc;

-- TODO: consider not including comps
/*
create view v_salesbydate
as
select sum(total) from v_sale group by dt order by date desc;
*/

-- sales by city by month
/*
select strftime('%Y-%m',dt) as yymm, lower(city) as cty, sum(total) as ttl 
from v_sale 
where cty in ('ridgefield','wilton') 
group by yymm, cty 
having ttl>0 
order by yymm,cty;
*/

create view vw_birthday as select id, firstname, lastname, emailaddress, phone, phone2, birthdate, 
strftime('%Y', date('now'))||'-'||strftime("%m-%d", birthdate) as birthday 
from cust;

-- custs with birthdays in next 7 days
--select * from vw_birthday where birthday > date('now') and birthday < date('now', '+7 days') order by birthday;

-- this selects riders with a birthday this week; if they are riding this week the classdate is shown (last col)
drop view vw_birthdaysthisweek;
create view vw_birthdaysthisweek
as
select b.id, b.firstname, b.lastname, b.emailaddress, b.phone, b.phone2, b.birthdate, b.birthday, a.classdate, 
    round(abs(julianday(a.classdate)-julianday(b.birthday))) as ndays
from vw_birthday b left outer join attend a on b.id=a.custid and (a.classdate >= date('now') and a.classdate <= date('now', '+7 days'))
where birthday >= date('now') and birthday <= date('now', '+7 days') order by birthday;

-- this selects riders who have a birthday this week and are riding on their birthday
drop view vw_birthdayriders;
create view vw_birthdayriders
as
select * from vw_birthdaysthisweek 
where date(birthday)=date(classdate)
order by birthdate;

-- super16 stuff
/*
select firstname, lastname, count(*) 
from attend 
where status='Enrolled' and date(classdate) >= '2014-07-01' and date(classdate) <= '2014-07-22' 
group by firstname, lastname 
having count(*) > 5 
order by lastname, firstname;
*/

-- 100 rider wall of joy stuff
/*
select firstname, lastname, count(*) as cnt, date(classdate) as asof from attend 
group by firstname, lastname 
order by lastname, firstname;
*/

-- attendance by customer by month
create view vw_attendbymonth as select custid, firstname, lastname, count(*) as cnt, strftime("%m-%Y", classdate) as mmyy from attend where status='Enrolled' group by custid, mmyy;

create view vw_toprideralltime as select custid, attend.firstname, attend.lastname, attend.emailaddress, 
phone, phone2, count(*) as cnt, date('2014-01-20') as start, 
date('now', '+1 days') as end 
from attend join cust on attend.custid=cust.id where status='Enrolled' and 
	classdate >=start and classdate <= end group by custid;

create view vw_attendlast31 as select custid, attend.firstname, attend.lastname, attend.emailaddress, 
phone, phone2, count(*) as cnt, date('now','-31 days') as start, 
date('now', '+7 days') as end 
from attend join cust on attend.custid=cust.id where status='Enrolled' and 
	classdate >=start and classdate <= end group by custid;

--note: we add 7 days here because the person might have future bookings; don't want to consider someone lapsed if they have lots of future bookings
	--drop view vw_attendlast30;
create view vw_attendlast30 as select custid, attend.firstname, attend.lastname, attend.emailaddress, 
phone, phone2, count(*) as cnt, date('now','-30 days') as start, 
date('now', '+7 days') as end 
from attend join cust on attend.custid=cust.id where status='Enrolled' and 
	classdate >=start and classdate <= end group by custid;

--drop view vw_attendprev30;
create view vw_attendprev30 as select custid, a.firstname, a.lastname, a.emailaddress,
phone, phone2, count(*) as cnt, date('now','-60 days') as start, 
date('now', '-30 days') as end 
from attend a join cust c on a.custid=c.id where status='Enrolled' and 
classdate >=start and classdate < end group by custid;

-- TODO: confirm working
drop view vw_doublesthisweek; 
create view vw_doublesthisweek
as
select custid, firstname, lastname, emailaddress, min(classdate) as firstclass, max(classdate) as lastclass, 
count(*) as cnt from attend where date(classdate)>=date('now') group by custid, date(classdate) 
having cnt > 1 order by classdate;

-- TODO: top riders query; just raw number of rides in past X days, not considering previous time period.


--drop view vw_riderstrendingup;
create view vw_riderstrendingup as 
select v1.custid, v1.firstname, v1.lastname, v1.emailaddress, v1.phone, v1.phone2, v1.cnt as prev30, v2.cnt as last30 
from vw_attendprev30 v1 left outer join vw_attendlast30 v2 on v1.custid=v2.custid 
where last30 > prev30 
order by last30-prev30 desc, last30 desc;

-- note: the complicated order by is designed to flag the best customers who are trending down
--drop view vw_riderstrendingdown;
create view vw_riderstrendingdown as 
select v1.custid, v1.firstname, v1.lastname, v1.emailaddress, v1.phone, v1.phone2, 
v1.cnt as prev30, v2.cnt as last30 from vw_attendprev30 v1 left outer join vw_attendlast30 v2 on v1.custid=v2.custid 
where prev30 > 0 and prev30 > last30 
order by (1.0*prev30)/(1*last30) * (prev30-last30) desc;

--drop view vw_riderslapsed;
create view vw_riderslapsed as 
select v1.custid, v1.firstname, v1.lastname, v1.emailaddress, v1.phone, v1.phone2,
v1.cnt as prev30 from vw_attendprev30 v1 left outer join vw_attendlast30 v2 on v1.custid=v2.custid 
where prev30 > 0 and v2.cnt is null 
order by prev30 desc;

drop view vw_riderslapsedtoday;
create view vw_riderslapsedtoday as 
select v1.custid, v1.firstname, v1.lastname, v1.emailaddress, v1.phone, v1.phone2,
v1.cnt as prev30 
from vw_attendprev30 v1 
  left outer join vw_attendlast31 v2 on v1.custid=v2.custid 
  left outer join vw_attendlast30 v3 on v1.custid=v3.custid 
where prev30 > 0 and v2.cnt is not null and v3.cnt is null 
order by prev30 desc;

-- list upcoming milestone riders (multiple of 50)
/*
drop view vw_milestone;
create view vw_milestone as select custid, a.firstname, a.lastname, a.emailaddress, phone, phone2, 
count(*) as cnt, max(classdate) as classdate 
from attend a join cust c on a.custid=c.id 
where status='Enrolled' and date(classdate)<=date('now','+10 day') 
group by custid having cnt % 50 = 0
order by cnt desc;
*/

select custid, a.firstname, a.lastname, a.emailaddress, phone, phone2, 
count(*) as cnt, max(classdate) as maxclassdate 
from attend a join cust c on a.custid=c.id 
where status='Enrolled' 
having date(maxclassdate)<=date('now','+10 day') 


-- see who's getting close to a multiple of 100
/*
drop view vw_wallofjoy;
create view vw_wallofjoy as
select custid, a.firstname, a.lastname, a.emailaddress, phone, phone2, 
count(*) as cnt, max(classdate) as classdate 
from attend a join cust c on a.custid=c.id 
where status='Enrolled' and date(classdate)<=date('now','+10 day') 
group by custid having (cnt > 90 and cnt <= 100) or (cnt > 190 and cnt <= 200) or (cnt > 290 and cnt <= 300)
or (cnt > 390 and cnt <= 400) or (cnt > 490 and cnt <= 500) or (cnt > 590 and cnt <= 600) or (cnt > 690 and cnt <= 700)
or (cnt > 790 and cnt <= 800) or (cnt > 890 and cnt <= 900) or (cnt > 990 and cnt <= 1000)
order by cnt desc;
*/

drop view vw_milestonenext7;
create view vw_milestonenext7
as
select custid, c.firstname, c.lastname, c.emailaddress, phone, phone2, classdate, num 
from attend join cust c on attend.custid=c.id 
where classdate between date('now') and date('now','+7 days') and ((num between 95 and 100) or (num between 195 and 200) or 
(num between 295 and 300) or (num between 395 and 400) or (num between 495 and 500) 
or (num between 595 and 600) or (num between 695 and 700) or 
(num between 795 and 800) or (num between 895 and 900) or 
(num between 995 and 1000)) order by c.lastname, c.firstname, classdate;

drop view vw_studiomilestonenext7;
create view vw_studiomilestonenext7
as
select custid, c.firstname, c.lastname, c.emailaddress, phone, phone2, classdate, num, totnum 
from attend join cust c on attend.custid=c.id 
where classdate between date('now') and date('now','+7 days') and totnum % 100 = 0
order by totnum;


/* TODO:
sqlite> select firstname, lastname, max(classdate) as maxclassdate, max(num) as maxnum from attend group by custid having maxclassdate < date('now') and maxnum between 97 and 100 union all select firstname, lastname, classdate, num from attend where classdate between date('now') and date('now','+8 days') and num between 97 and 100 order by lastname, firstname, classdate;

*/


/* TODO: improve wall of joy stuff
sqlite> create index idx_attend_classdate on attend(classdate);sqlite> select id, firstname, lastname, classdate, (select count(*) from attend a2 where status='Enrolled' and a2.custid=a.custid and a2.classdate<=a.classdate) as num from attend a where a.classdate between date('now','-7 days') and date('now','+7 days') and status='Enrolled' and (num between 95 and 100) or (num between 195 and 200) or (num between 295 and 300) or (num between 395 and 400) or (num between 495 and 500) or (num between 595 and 600) order by lastname, firstname, classdate;
^CError: interrupted
sqlite> create table temp as select id, firstname, lastname, classdate, (select count(*) from attend a2 where status='Enrolled' and a2.custid=a.custid and a2.classdate<=a.classdate) as num from attend a;^CError: interrupted
sqlite> create table temp as select id, firstname, lastname, classdate, (select count(*) from attend a2 where status='Enrolled' and a2.custid=a.custid and a2.classdate<=a.classdate) as num from attend a where date(a.classdate) between date('now','-7 days') and date('now','+7 days') and status='Enrolled';
sqlite> select * from temp;

*/

--select custid, firstname, lastname, count(*) as cnt, max(classdate) as maxclassdate from attend where status='Enrolled' and date(classdate)<=date('now','+20 days') group by custid;


--create view v_totalsalesbyitem as select item, sum(total) from sale group by item order by sum(total) desc;

--TODO: create new customers query too

drop view vw_customersalesalltime;
create view vw_customersalesalltime as 
select custid, c.firstname, c.lastname, c.emailaddress, c.phone, c.phone2, count(*) as cnt, sum(total) as total 
from sale join cust c on sale.custid=c.id 
where pmtype != 'Comp'
group by custid order by total desc;

drop view vw_customersaleslast30;
create view vw_customersaleslast30 as 
select custid, c.firstname, c.lastname, c.emailaddress, c.phone, c.phone2, count(*) as cnt, sum(total) as total 
from sale join cust c on sale.custid=c.id 
where pmtype != 'Comp' and date(dt) >= date('now', '-30 days')
group by custid order by total desc;

drop view vw_customersaleslast7;
create view vw_customersaleslast7 as 
select custid, c.firstname, c.lastname, c.emailaddress, c.phone, c.phone2, count(*) as cnt, sum(total) as total 
from sale join cust c on sale.custid=c.id 
where pmtype != 'Comp' and date(dt) >= date('now', '-7 days')
group by custid order by total desc;

drop view vw_itemsaleslastalltime;
create view vw_itemsalesalltime as 
select item, count(*) as cnt, sum(total) as total 
from sale 
where pmtype != 'Comp' 
group by item order by total desc;

drop view vw_itemsaleslast30;
create view vw_itemsaleslast30 as 
select item, count(*) as cnt, sum(total) as total 
from sale 
where pmtype != 'Comp' and date(dt) >= date('now', '-30 days')
group by item order by total desc;

drop view vw_itemsaleslast7;
create view vw_itemsaleslast7 as 
select item, count(*) as cnt, sum(total) as total 
from sale 
where pmtype != 'Comp' and date(dt) >= date('now', '-7 days')
group by item order by total desc;

drop view vw_totalsaleslast30;
create view vw_totalsaleslast30 as 
select count(*) as cnt, sum(total) as total 
from sale 
where pmtype != 'Comp' and date(dt) >= date('now', '-30 days');

drop view vw_totalsaleslast7;
create view vw_totalsaleslast7 as 
select count(*) as cnt, sum(total) as total 
from sale 
where pmtype != 'Comp' and date(dt) >= date('now', '-7 days');

drop view vw_compslast7;
create view vw_compslast7 as 
select dt, custid, c.firstname, c.lastname, c.emailaddress, c.phone, c.phone2, count(*) as cnt, item, total 
from sale join cust c on sale.custid=c.id 
where (pmtype == 'Comp' or total=0) and date(dt) >= date('now', '-7 days')
group by custid, item order by item, dt desc;

drop view vw_refundslast7;
create view vw_refundslast7 as 
select dt, custid, c.firstname, c.lastname, c.emailaddress, c.phone, c.phone2, item, pmtype, total
from sale join cust c on sale.custid=c.id 
where total < 0 and date(dt) >= date('now', '-7 days');

drop view vw_salestypesalltime;
create view vw_salestypesalltime as 
select count(*) as cnt, sum(total) as ttl, typ from sale group by typ;

drop view vw_salestypeslast30;
create view vw_salestypeslast30 as 
select count(*) as cnt, sum(total) as ttl, typ from sale where dt >= date('now', '-30 days') group by typ;

drop view vw_salestypeslast7;
create view vw_salestypeslast7 as 
select count(*) as cnt, sum(total) as ttl, typ from sale where dt >= date('now', '-7 days') group by typ;


--select custid, a.firstname, a.lastname, a.emailaddress, phone, phone2, count(*) as cnt, max(classdate) as classdate from attend a join cust c on a.custid=c.id where status='Enrolled' group by custid having (cnt > 90 and cnt <= 100) 

-- get new customers as of a particular day
select id, firstname, lastname, emailaddress, phone, phone2, datecreated, birthdate, age, city
from vw_cust
where date(datecreated) = date('now','-1 day');

-- TODO: new riders who haven't signed up for a class yet
-- TODO: need to exclude fashion show people
sqlite> select c.id, c.firstname, c.lastname, c.emailaddress, c.phone, c.phone2, c.datecreated, a.classdate from cust c left outer join attend a on c.id=a.custid where date(datecreated) > date('now', '-7 days') and classdate is null;

-- TODO: fashion show counts


-- number of customers of each age
drop view vw_numcustbyage;
create view vw_numcustbyage as select age, count(*) as cnt from vw_cust group by age order by age desc;

-- number of customers by age bracket
-- None, 0-20, 21-30, 31-40, 41-50, 51-60, 61-70, 70+
/*
select 
  (select sum(cnt) from vw_numcustbyage where age is null) as none,
  (select sum(cnt) from vw_numcustbyage where age between 0 and 20) as age_0_20,
  (select sum(cnt) from vw_numcustbyage where age between 21 and 30) as age_21_30,
  (select sum(cnt) from vw_numcustbyage where age between 31 and 40) as age_31_40,
  (select sum(cnt) from vw_numcustbyage where age between 41 and 50) as age_41_50,
  (select sum(cnt) from vw_numcustbyage where age between 51 and 60) as age_51_60,
  (select sum(cnt) from vw_numcustbyage where age between 61 and 70) as age_61_70,
  (select sum(cnt) from vw_numcustbyage where age > 70) as age_70_plus;
*/

create view vw_numcustbyagerange 
as
select 'no birthday', sum(cnt) from vw_numcustbyage where age is null union all
select '0-12', sum(cnt) from vw_numcustbyage where age between 0 and 12 union all
select '13-19', sum(cnt) from vw_numcustbyage where age between 13 and 19 union all
select '20-29', sum(cnt) from vw_numcustbyage where age between 20 and 29 union all
select '30-39', sum(cnt) from vw_numcustbyage where age between 30 and 39 union all
select '40-49', sum(cnt) from vw_numcustbyage where age between 40 and 49 union all
select '50-59', sum(cnt) from vw_numcustbyage where age between 50 and 59 union all
select '60-69', sum(cnt) from vw_numcustbyage where age between 60 and 69 union all
select '70+', sum(cnt) from vw_numcustbyage where age >= 70;

-- TODO: number of rides by age range

drop view vw_numridesbyage;
create view vw_numridesbyage
as
select c.age, count(*) as cnt from attend a join vw_cust c on a.custid=c.id where a.status='Enrolled' group by c.age order by c.age;

create view vw_numridesbyagerange
as
select 'no age', sum(cnt) from vw_numridesbyage where age is null union all
select '0-12', sum(cnt) from vw_numridesbyage where age between 0 and 12 union all
select '13-19', sum(cnt) from vw_numridesbyage where age between 13 and 19 union all
select '20-29', sum(cnt) from vw_numridesbyage where age between 20 and 29 union all
select '30-39', sum(cnt) from vw_numridesbyage where age between 30 and 39 union all
select '40-49', sum(cnt) from vw_numridesbyage where age between 40 and 49 union all
select '50-59', sum(cnt) from vw_numridesbyage where age between 50 and 59 union all
select '60-69', sum(cnt) from vw_numridesbyage where age between 60 and 69 union all
select '70+', sum(cnt) from vw_numridesbyage where age >= 70;


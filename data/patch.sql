drop view vw_birthdaysthisweek;
create view vw_birthdaysthisweek
as
select b.id, b.firstname, b.lastname, b.emailaddress, b.phone, b.phone2, b.birthdate, b.birthday, a.classdate 
from vw_birthday b left outer join attend a on b.id=a.custid and (a.classdate >= date('now') and a.classdate <= date('now', '+7 days'))
where birthday >= date('now') and birthday <= date('now', '+7 days') order by birthday;

-- this selects riders who have a birthday this week and are riding on their birthday
drop view vw_birthdayriders;
create view vw_birthdayriders
as
select * from vw_birthdaysthisweek 
where date(birthday)=date(classdate)
order by birthdate;

drop view vw_attendfuture;
create view vw_attendfuture as select custid, attend.firstname, attend.lastname, attend.emailaddress, 
phone, phone2, date('now') as start, date('now', '+7 days') as end, attend.classdate 
from attend join cust on attend.custid=cust.id where status='Enrolled' and 
	classdate >=start and classdate <= end group by custid;



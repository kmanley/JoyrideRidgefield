CREATE TABLE occ (dt datetime, site string, instr string, unavail int, total int, primary key (dt, site));
create view v_occ as select *, 1.0*unavail/total*100.0 as pct from occ;
create view v_date as select date(dt) as dt, site, count(*) as cnt, sum(unavail) as unavail, sum(total) as total, avg(pct) as pct from v_occ group by date(dt), site;

# get average occupancy by instructor
select inst, count(*), avg(pct) as avgpct from v_occ group by inst order by avgpct desc;

# get overall stats by site by date
select date(dt), site, avg(pct) from v_occ group by date(dt), site;
or
select * from v_date where dt='2014-07-08';

/* TODO: aggregate stats over different time periods

sqlite> 
sqlite> select site, sum(cnt) as ttlcnt, sum(unavail) as ttlunavail, sum(total) as ttltotal from v_date
   ...> group by site where dt between date('now', '-7 days') and date('now');
Error: near "where": syntax error
sqlite> select site, sum(cnt) as ttlcnt, sum(unavail) as ttlunavail, sum(total) as ttltotal from v_date
   ...> where dt between date('now', '-7 days') and date('now') group by site order by site;
sqlite> 
sqlite> where dt between date('now', '-60 days') and date('now') group by site order by site;
Error: near "where": syntax error
*/

drop view vw_occalltime;
create view vw_occalltime
as
select site, count(*) as numclasses, sum(unavail) as enrolled, 
sum(total) as avail, round(cast(sum(unavail) as float) / count(*),1) as ridersperclass, 
round(avg(pct),1) as occupancy from v_occ group by site;

drop view vw_occyymm;
create view vw_occyymm
as
select strftime('%Y-%m',dt) as yymm, site, count(*) as numclasses, 
sum(unavail) as enrolled, 
sum(total) as avail, 
round(cast(sum(unavail) as float)/(min(julianday(date('now', 'localtime')), julianday(date(dt, 'start of month','localtime', '+1 month', '-1 day'))) - julianday(date(dt, 'localtime', 'start of month')) + 1),1) as ridersperday,
round(cast(sum(unavail) as float) / count(*),1) as ridersperclass, 
round(avg(pct),1) as occupancy from v_occ 
group by yymm, site;


drop view vw_occyymmbyinstr;
create view vw_occyymmbyinstr
as
select strftime('%Y-%m',dt) as yymm, site, case when substr(instr,1,7)='Stacia' then instr when substr(instr,1,1)=='S' then substr(instr,2) else instr end as instrex, count(*) as numclasses, sum(unavail) as enrolled, 
sum(total) as avail, round(cast(sum(unavail) as float) / count(*),1) as ridersperclass, 
round(avg(pct),1) as occupancy from v_occ 
group by yymm, site, instrex;




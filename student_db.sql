create table student(
	id SERIAL PRIMARY KEY,
	name TEXT NOT NULL,
	age INT,
	email TEXT NOT NULL
)
select * from student;
select id,email from student;
insert into student(name,age,email)values('mohana',20,'mohana@email.com');
insert into student(name,age,email)values('srinivas',30,'srinivas@email.com');
update student set email = 'srinu@email.com'
where id =2
delete from student where id =1


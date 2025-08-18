create table if not exists rooms(
    id integer unique primary key not null,
    name varchar(32) unique not null
);

create table if not exists students(
    id integer unique primary key not null,
    name varchar(64) not null,
    sex varchar(1),
    birthday TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    room integer REFERENCES rooms(id) ON DELETE SET NULL
);

create index idx_students_room on students(room);
create index idx_students_room_birthday on students(room, birthday);
create index idx_students_room_sex on students(room, sex);
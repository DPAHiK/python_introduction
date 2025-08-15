create table if not exists rooms(
    id integer unique primary key not null,
    name varchar(32) not null
);

create table if not exists students(
    id integer unique primary key not null,
    name varchar(64) not null,
    sex varchar(1),
    birthday TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    room integer REFERENCES rooms(id) ON DELETE SET NULL
);
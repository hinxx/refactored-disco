drop table if exists entries;
create table entries (
  id integer primary key autoincrement,
  title text not null,
  'text' text not null
);

DROP TABLE IF EXISTS Frames;
CREATE TABLE Frames (
  Type TEXT NOT NULL,
  Stamp TEXT NOT NULL,
  Signal BLOB NOT NULL
);

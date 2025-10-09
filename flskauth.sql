---まずPostgreSQLを起動して、次のSQLを実行すること。
create table flskauth(
  uid serial primary key,
  uname text not null,
  email text not null,
  pw text not null) without oids;

#!/bin/bash



if [ $(id -u) -eq 0 ]; then
        su db2inst1

        echo "Connecting to the bank database\n"
        exec db2 connect to database bank as user db2inst1 password password


        echo "granting the redbook user permissions\n"
        exec db2 GRANT DBADM, CREATETAB, BINDADD, CONNECT, CREATE_NOT_FENCED, IMPLICIT_SCHEMA, LOAD ON DATABASE TO USER redbook

        exit 0
else
        echo "Only root may add a user to the system."
        exit 2
#!/bin/bash

username="redbook"
password="password"


if [ $(id -u) -eq 0 ]; then
        egrep "^$username" /etc/passwd >/dev/null
        if [ $? -eq 0 ]; then
                echo "Username $username already exists!"
        else
                useradd -m -p "$password" "$username"
                [ $? -eq 0 ] && echo "User has been added to system!" || echo "Failed to add a user!"
        fi

        su db2inst1

        echo "Connecting to the bank database\n"
        db2 connect to database bank as user db2inst1 password password


        echo "granting the redbook user permissions\n"
        db2 GRANT DBADM, CREATETAB, BINDADD, CONNECT, CREATE_NOT_FENCED, IMPLICIT_SCHEMA, LOAD ON DATABASE TO USER redbook

        exit 0
else
        echo "Only root may add a user to the system."
        exit 2
fi

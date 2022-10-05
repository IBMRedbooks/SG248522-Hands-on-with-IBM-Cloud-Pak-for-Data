#!/bin/sh

username="test"
password="password"

if [ $(id -u) -eq 0 ]; then
        egrep "^$username" /etc/passwd >/dev/null
        if [ $? -eq 0 ]; then
                echo "Username $username already exists!"
        else
                useradd -m "$username"
                [ $? -eq 0 ] && echo "User has been added to system!" || echo "Failed to add a user!"
                echo -e "${username}:${password}" | chpasswd 
        fi

        source /home/db2inst1/.bashrc

        echo "Connecting to the bank database\n"
        db2 connect to bank user db2inst1 using password


        echo "granting the test user permissions on the bank database\n"
        db2 GRANT DBADM, CREATETAB, BINDADD, CONNECT, CREATE_NOT_FENCED, IMPLICIT_SCHEMA, LOAD ON DATABASE TO USER test

        exit 0
else
        echo "Only root may add a user to the system."
        exit 2
fi

#!/bin/sh



if [ $(id -u) -eq 0 ]; then
        
        source /home/db2inst1/.bashrc

        echo "Connecting to the bank database\n"
        db2 connect to bank user db2inst1 using password

        echo "Executing the lineage settings script\n"
        db2 -tvmf lineage-settings.sql
        exit 0
else
        echo "Only root may add a user to the system."
        exit 2
fi

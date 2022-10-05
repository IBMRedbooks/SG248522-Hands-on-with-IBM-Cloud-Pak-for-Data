#!/bin/sh

basedir=$(pwd)


##Create database and import
su -c "${basedir}/run_bank.sh" - db2inst1

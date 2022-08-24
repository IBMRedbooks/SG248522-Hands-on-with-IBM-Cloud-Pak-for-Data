SET SCHEMA SYSTOOLS;

BEGIN
declare ret int;
call SYSPROC.DB2LK_GENERATE_DDL ('-e -td ; -z "SYSIBM" -tw "DUAL"',
ret); 
END


GRANT EXECUTE ON PROCEDURE SYSPROC.DB2LK_GENERATE_DDL TO USER redbook;
GRANT EXECUTE ON PROCEDURE SYSPROC.DB2LK_CLEAN_TABLE TO USER redbook;
GRANT ALL ON SYSTOOLS.DB2LOOK_INFO to user redbook;
GRANT USAGE ON WORKLOAD SYSDEFAULTUSERWORKLOAD TO USER redbook;
GRANT USAGE ON SEQUENCE SYSTOOLS.DB2LOOK_TOKEN TO user redbook;
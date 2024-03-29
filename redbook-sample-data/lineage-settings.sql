SET SCHEMA SYSTOOLS;

CALL SYSPROC.DB2LK_GENERATE_DDL('-e -t myschema.mytable', ?);

GRANT EXECUTE ON PROCEDURE SYSPROC.DB2LK_GENERATE_DDL TO USER redbook;
GRANT EXECUTE ON PROCEDURE SYSPROC.DB2LK_CLEAN_TABLE TO USER redbook;

GRANT ALL ON SYSTOOLS.DB2LOOK_INFO TO USRE redbook;

GRANT USAGE ON WORKLOAD SYSDEFAULTUSERWORKLOAD TO USER redbook;
GRANT USAGE ON SEQUENCE SYSTOOLS.DB2LOOK_TOKEN TO USER redbook;
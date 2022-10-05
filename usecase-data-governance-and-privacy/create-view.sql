SET SCHEMA BANK2;

CREATE VIEW ACCOUNT_CUSTOMER_RELATIONSHIP
AS
    SELECT
        a.ACCOUNT_ID,
        a.ACCOUNT_TYPE,
        a.ACCOUNT_BALANCE,
        c.NAME,
        c.ADDRESS,
        c.GENDER, 
        c.MARITAL_STATUS,
        c.EMAIL
    FROM BANK_ACCOUNTS  a
        INNER JOIN BANK_CUSTOMERS c 
            ON c.customer_id = a.customer_id;
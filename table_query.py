drop_codes = '''
    DROP TABLE IF EXISTS "codes";
'''
drop_NYSE = '''
    DROP TABLE IF EXISTS "NYSE";
'''

create_codes = """
    CREATE TABLE IF NOT EXISTS "codes" (
        "id"	INTEGER PRIMARY KEY AUTOINCREMENT,
        "code"	TEXT NOT NULL UNIQUE
    );
"""
create_NYSE = """
    CREATE TABLE IF NOT EXISTS "NYSE" (
        "id" INTEGER PRIMARY KEY AUTOINCREMENT, 
        "code_id" INTEGER, 
        "name" TEXT NOT NULL, 
        "url" TEXT NOT NULL, 
        FOREIGN KEY("code_id") REFERENCES "codes"("id") 
    );
"""

insert_codes = """
    INSERT INTO codes
    VALUES (NULL, ?)
"""

insert_NYSE = """
    INSERT INTO NYSE
    VALUES (NULL, ?, ?, ?)
"""

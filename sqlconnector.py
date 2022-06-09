import mysql.connector

try:
    with mysql.connector.connect(
        host = "localhost",
        user = "root",
        password = "testpwd123",
        database = "ratingsdb"
    ) as connection:
        print(connection)
        #createTable("Sections", keys, keysTypes)
except mysql.connector.Error as e:
    print(e)

connection = mysql.connector.connect(
    host = "localhost",
    user = "root",
    password = "testpwd123",
    database = "ratingsdb"
)

def createTable(name, keys, keysTypes):
    sqlDataTypes = {int: "INT", float: "FLOAT", str: "VARCHAR(10)", "text": "LONGTEXT"}

    try:
        createTableQuery = "CREATE TABLE IF NOT EXISTS {0}(id INT AUTO_INCREMENT PRIMARY KEY)".format(name, keys)
        connection.cursor().execute(createTableQuery)
        connection.commit()
    except mysql.connector.Error as e:
        print(e)

    for i in range(0,len(keys)):
        addColumnQuery = "ALTER TABLE {0} ADD COLUMN `{1}` {2}".format(name, keys[i], sqlDataTypes[keysTypes[i]])
        connection.cursor().execute(addColumnQuery)
        connection.commit()

def enterTopicsDB(entries, name):
    try:
        entries[0]["topics"]
        many = True
    except:
        many = False
    
    for i in range(0, len(entries)):
        dept = entries[i]["dept"]
        entry = list(entries[i]["topics"].items())
        
        attributeQuery = ""
        for i in range(0, len(keys)):
            attributeQuery += "`{0}`, ".format(keys[i]) 
        attributeQuery = attributeQuery[:-2]
        
        insertQuery = """
        INSERT INTO {0} ({2})
        VALUES ({1})
        """.format(name, "%s, %s, %s", attributeQuery)
        entry = [(dept, ) + course for course in entry]
        print(len(entry))
        print(entry[0])
        with connection.cursor() as cursor:
            print("pushing values")
            try:
                cursor.executemany(insertQuery, entry)
                connection.commit()
            except mysql.connector.Error as e:
                print(e)
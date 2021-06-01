import os
import sqlite3 as sql
from os.path import basename
from typing import List, Tuple


class Database:
    """A class used to wrap python sqlite module.

    This class uses the python sqlite3 module to build a robust database. Functions
    often use an easier interface than SQLite itself, and are more matched with the
    main simulator.

    ...

    Attributes:
        name (str): Name of the sql database file.
        conn (Connection): SQLite connection to the database.
        cur (Cursor): SQL cursor of the database.
        url (str): URL of the database file in data folder.

    """

    def __init__(self, name: str):
        """Initialize a database with the given name inside the data/sql folder.

        Args:
            name (str): The database name.

        Raises:
            FileNotFoundError: In case current working directory is neither src nor example,
            and not even the project directory, a file not found exception will be thrown.
        """
        self.name = name

        # connect to sql database in data folder from main working dir
        folder_name = 'sql'
        if basename(os.path.abspath(os.path.join(os.getcwd(), os.pardir))) == 'Pyfectious':
            self.url = os.path.join(os.path.join(os.getcwd(), os.pardir, 'data', folder_name), self.name)
        elif basename(os.getcwd()) == 'Pyfectious':
            self.url = os.path.join(os.path.join(os.getcwd(), 'data', folder_name), self.name)
        else:
            raise FileNotFoundError('Run the source in "project", "src", or "example" folder!')

        self.url += '.sqlite3'

        # build the connection and cursor
        self.conn = sql.connect(self.url)
        self.cur = self.conn.cursor()

        # enable async mode
        self.conn.execute('PRAGMA synchronous = OFF')

    def create_table(self, name: str, columns: List[Tuple[str, str]]):
        """ Create a table by names and columns and columns' type list.

        Args:
            name (str): Name of the table.
            columns (List[Tuple[str, str]]): Columns name and type.
        """
        query_data = ""

        # build the right sql order
        for col in columns:
            query_data += col[0] + ' ' + col[1] + ','

        # remove the last colon
        query_data = query_data[0: len(query_data) - 1]

        # execute the query and commit
        self.cur.execute("CREATE TABLE IF NOT EXISTS {}({})".format(name, query_data))
        self.commit()

    def insert(self, table_name: str, data: List):
        """Insert a single data into the table.

        Args:
            table_name (str): Name of the target table for the insertion.
            data (List): The data to be inserted.
        """
        query_data = ""

        # build the right sql order
        for item in data:
            query_data += "'" + item + "'" + ','

        # remove the last colon
        query_data = query_data[0: len(query_data) - 1]

        # execute the query
        self.cur.execute("INSERT INTO {} VALUES({})".format(table_name, query_data))

    def insert_many(self, table_name: str, data_list: List):
        """Insert a batch of data rows into the table at once.

        Args:
            table_name (str): The target table name.
            data_list (List): A 2 dimensional list for insertion operation.
        """
        # create wildcard for data len
        wild_cards = ""
        for _ in range(len(data_list[0])):
            wild_cards += "?,"
        wild_cards = wild_cards[0: len(wild_cards) - 1]

        # execute the data at once
        self.cur.executemany("INSERT INTO {} VALUES({})".format(table_name, wild_cards), data_list)

    def commit(self):
        """Perform a connection commit.

        Since commit is time consuming, this is for the times of a batch operation,
        followed by a commit.
        """
        # perform a commit to database
        self.conn.commit()

    def remove(self, table_name: str, condition="1"):
        """Remove a certain data from the table.

        Args:
            table_name (str): The target table name.
            condition (str, optional): If any specific data needs to be removed, a
            conditional statement may be passed here. Defaults to "1".
        """
        self.cur.execute("DELETE FROM {} WHERE {}".format(table_name, condition))
        self.commit()

    def update(self, table_name: str, columns: List[Tuple[str, str]], condition="1"):
        """Perform a table update on values based on the condition.

        Args:
            table_name (str): The target table name.
            columns (List[Tuple[str, str]]): The columns that have to be updated.
            condition (str, optional): If any specifications is required, set the
            condition value to a SQLite conditional statement. Defaults to "1".
        """
        query_data = ""

        # build the right sql order
        for col in columns:
            query_data += col[0] + " " + col[1] + ","

        # remove the last colon
        query_data = query_data[0: len(query_data) - 1]

        # execute the query
        self.cur.execute("UPDATE {} SET {} WHERE {}".format(table_name, query_data, condition))
        self.commit()

    def get_data(self, table_name: str, data="*", condition="1", condition_data: Tuple = None) -> List[str]:
        """ Returns the data from table based on a condition.

        Args:
            table_name (str): The target table name.
            data (str, optional): Which column has to be returned. Defaults to "*".
            condition (str, optional): If any conditions is necessary on the retrieved data,
            a conditional statement may be passed. Defaults to "1".
            condition_data (Tuple, optional): Condition data in case the condition uses wildcards.
            Defaults to (None).

        Returns:
            List[str]: A list of the acquired database rows.
        """
        if condition_data is None:
            self.cur.execute("SELECT {} FROM {} WHERE {}".format(data, table_name, condition))
        else:
            self.cur.execute("SELECT {} FROM {} WHERE {}".format(data, table_name, condition), condition_data)

        return self.cur.fetchall()

    def count_data(self, table_name: str, data="*", count_data="*", condition="1", condition_data: Tuple = None) -> \
    List[str]:
        """ Returns the count of data from table based on a condition.

        Args:
            table_name (str): The target table name.
            data (str, optional): Which column count has to be returned. Defaults to "*".
            count_data (str, optional): Which column count has to be returned. Defaults to "*".
            condition (str, optional): If any conditions is necessary on the retrieved data,
            a conditional statement may be passed. Defaults to "1".
            condition_data (Tuple, optional): Condition data in case the condition uses wildcards.
            Defaults to (None).

        Returns:
            List[str]: A list of the acquired database rows.
        """
        if condition_data is None:
            self.cur.execute("SELECT {}, COUNT({}) FROM {} WHERE {}".format(data, count_data, table_name, condition))
        else:
            self.cur.execute("SELECT {}, COUNT({}) FROM {} WHERE {}".format(data, count_data, table_name, condition),
                             condition_data)

        return self.cur.fetchall()

    def get_tables(self) -> List[str]:
        """Returns the names of all tables.

        Returns:
            List[str]: Name of all the tables in the database.
        """
        self.cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        return self.cur.fetchall()

    def delete_data(self, table_name: str, condition="1"):
        """Delete data based on SQL condition.

        Args:
            table_name (str): Name of the target table.
            condition (str, optional): If needed, any SQL condition may be
            passed to the function to delete specific data. Defaults to 1.
        """
        self.cur.execute("DELETE FROM {} WHERE {}".format(table_name, condition))
        self.commit()

    def drop_table(self, table_name: str):
        """Drop a specific table using its name.

        Args:
            table_name (str): Name of the target table.
        """
        self.cur.execute("DROP TABLE {}".format(table_name))
        self.commit()

    def drop_database(self, db_name: str):
        """Drop a database completely.

        Args:
            db_name (str): The target database name.
        """
        self.cur.execute("DROP DATABASE {}".format(db_name))
        self.commit()

    def close(self):
        """Close the database connection.
        """
        self.cur.close()
        self.conn.close()


# main
if __name__ == '__main__':
    # implement a local test

    print("Test initiated")

    # create the database
    db = Database('example')
    db.create_table('test_table', [('c1', 'str'), ('c2', 'int')])

    # example the main functions
    db.insert('test_table', ['test_str1', '123'])
    db.insert('test_table', ['test_str2', '124'])

    # retrieve from db
    print(db.get_data('test_table'))

    # remove a data
    db.remove('test_table', 'c1="test_str1"')

    # retrieve from db
    print(db.get_data('test_table'))

    # get table name
    print(db.get_tables())

    # disconnect
    db.close()

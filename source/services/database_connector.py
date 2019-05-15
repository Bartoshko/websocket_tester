import mysql.connector
import json
from subprocess import Popen
from threading import Event


class DataBaseConnector:
    """
    DataBaseConnector class is responsible for connection and communication
    with database.
    Checks if local db configuration hash is compatible with
    application db tables configuration
    Updates db schema if needed.
    Makes backup in application db.
    Sets sinks, anchors, tags configuration in db.
    Restores db to last backup.
    """

    __back_up_is_made = False
    __floor_number = None
    __db = None
    __cursor = None

    @staticmethod
    def read_from_db_hash_file(path):
        with open(path, 'r', encoding='utf-8') as file:
            return json.load(file)

    def __init__(self, db_configuration):
        self.__db_configuration = db_configuration
        self.__tables = tuple(self.__get_tables())
        self.__db_description = tuple(self.__get_db_description())

    def __del__(self):
        del self.__tables
        del self.__db_description
        del self.__back_up_is_made
        del self.__floor_number
        del self.__db
        del self.__cursor

    @property
    def tables(self):
        return self.__tables

    def test_db_hash(self, path):
        base_hash_configurations = DataBaseConnector.read_from_db_hash_file(path)
        actual_db_configuration = self.get_db_configuration()
        for base, actual in zip(base_hash_configurations, actual_db_configuration):
            assert base == actual, \
                'DB hash stored in emulator configuration and actual DB structure are incoherent.' \
                ' {} is not equal {}'.format(base, actual)

    def get_db_configuration(self):
        return self.__db_description

    def set_floor_for_test(self, floor_number):
        if not self.__check_if_floor_exists_in_db(floor_number):
            self.__insert_floor_into_db(floor_number)
        self.__floor_number = floor_number

    def create_fresh_db_hash(self, path):
        for table in self.__db_description:
            print('database configuration hash created for {}'.format(table))
        with open(path, 'w', encoding='utf-8') as file:
            json.dump(self.__db_description, file)

    def back_up_db(self):
        event_waiter = Event()
        try:
            dump_process = Popen('mysqldump -h {} -P 3306 -u {} {} > backup.sql'.format(
                self.__db_configuration['host'],
                self.__db_configuration['user'],
                self.__db_configuration['database']
            ), shell=True)
            while not event_waiter.isSet():
                if dump_process.poll() is not None:
                    dump_process.terminate()
                    event_waiter.set()
                    self.__back_up_is_made = True
        except EnvironmentError:
            print('Cannot dump database')

    def reload_from_db_back_up(self):
        event_waiter = Event()
        try:
            restore_process = Popen('mysql -u %s -h %s %s < backup.sql' %
                                    (self.__db_configuration['user'],
                                     self.__db_configuration['host'],
                                     self.__db_configuration['database']),
                                    shell=True)
            while not event_waiter.isSet():
                if restore_process.poll() is not None:
                    restore_process.terminate()
                    event_waiter.set()
        except EnvironmentError:
            print('Cannot restore database')

    def delete_all_records_from_tables(self, tables):
        """
        This method is closing cursor
        for each of tree steps as after FOREIGN_KEY_CHECKS change in db
        to ensure DB Lock is freed and DB has new settings
        """
        if type(tables) is not tuple:
            raise ValueError('Wrong argument type, passed to delete_all_records_from_tables method')
        self.start_new_db_connection()
        try:
            self.__cursor.execute("SET FOREIGN_KEY_CHECKS=0")
            for table in tables:
                if type(table) is str:
                    self.__cursor.execute("TRUNCATE TABLE {}".format(table))
            self.__cursor.execute("SET FOREIGN_KEY_CHECKS=1")
        except ValueError as error_0:
            print(error_0)
        finally:
            self.commit_to_db_and_close_connection()

    def start_new_db_connection(self):
        self.__db = mysql.connector.connect(**self.__db_configuration)
        self.__cursor = self.__db.cursor()

    def commit_to_db_and_close_connection(self):
        self.__db.commit()
        self.__cursor.close()
        self.__db.close()

    def insert_to_db(self, table, columns, values):
        if self.__db is not None and self.__cursor is not None:
            if not self.__back_up_is_made:
                raise ValueError('DataBase is not backed up properly')
            if type(values) is not tuple or type(columns) is not tuple or type(table) is not str:
                raise ValueError('Wrong values passed to db insert method')
            if len(columns) == len(values):
                column_names_for_command = ", ".join([v for v in columns])
                values_string_fields = ", ".join('%s' for _ in range(len(values)))
                command_composition = ("INSERT INTO {} "
                                       "({}) "
                                       "VALUES ({})".format(table, column_names_for_command, values_string_fields)
                                       )
                try:
                    self.__cursor.execute(command_composition, values)
                except ValueError as error:
                    print(error)
            else:
                raise ValueError('Number of columns is not equal to number of values')
        else:
            raise ValueError('Set connection to db before executing insertion')

    def get_device_id(self, short_id):
        if self.__db is not None and self.__cursor is not None:
            device_id = None
            try:
                self.__cursor.execute("SELECT id FROM device WHERE shortId= {}".format(short_id))
                device_id = self.__cursor.fetchone()
            except ValueError as error:
                print(error)
            finally:
                return device_id
        else:
            raise ValueError('Set connection to db before executing insertion')

    def __check_if_floor_exists_in_db(self, floor_number_to_check):
        self.start_new_db_connection()
        checked_floor = []
        try:
            self.__cursor.execute("SELECT 1 FROM {} WHERE id= {}".format('floor', floor_number_to_check))
            checked_floor = self.__cursor.fetchall()
        except ValueError as error:
            print(error)
        finally:
            self.commit_to_db_and_close_connection()
            return len(checked_floor) > 0

    def __insert_floor_into_db(self, number):
        self.start_new_db_connection()
        try:
            self.__cursor.execute("INSERT INTO floor (id) VALUES ({})".format(number))
        except ValueError as error:
            print(error)
        finally:
            self.commit_to_db_and_close_connection()

    def __get_tables(self):
        self.start_new_db_connection()
        tables = []
        try:
            self.__cursor.execute("SHOW TABLES")
            for item in self.__cursor:
                tables.append(item)
            tables = [item for sublist in map(lambda x: [x], tables) for item in sublist]
        except ValueError as error:
            print(error)
        finally:
            self.commit_to_db_and_close_connection()
            return tables

    def __get_db_description(self):
        description = []
        for table in self.__tables:
            description.append({table[0]: self.__get_table_description(table)})
        return description

    def __get_table_description(self, table):
        self.start_new_db_connection()
        description = []
        try:
            self.__cursor.execute("DESCRIBE {}".format(table))
            for item in self.__cursor:
                # item is returned as a set but we want list to have more method available for unit tests
                item = list(item)
                description.append(item)
        except ValueError as error:
            print(error)
        finally:
            self.commit_to_db_and_close_connection()
            return description

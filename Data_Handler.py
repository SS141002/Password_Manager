from sqlite3 import *
from hashlib import sha3_512
from secrets import choice
from base64 import b64encode
from cryptography.fernet import Fernet


class Data:
    @staticmethod
    def open():
        global con
        global cr

        con = connect("PMS.db")
        cr = con.cursor()

    @staticmethod
    def exec(*args):
        cr.execute(*args)

    @staticmethod
    def save():
        con.commit()

    @staticmethod
    def close():
        con.close()

    @staticmethod
    def getone():
        return cr.fetchone()

    @staticmethod
    def getmany(num):
        return cr.fetchmany(num)

    @staticmethod
    def getall():
        return cr.fetchall()

    @staticmethod
    def open_close(*args):
        Data.open()
        for i in args:
            i()
            Data.save()
        Data.close()
        del args

    ####################################################################################################################

    @staticmethod
    def create_database():
        Data.exec('''CREATE TABLE IF NOT EXISTS USER 
            (fname STRING (128) NOT NULL CHECK (length(fname) <= 128),
            lname STRING (128) NOT NULL CHECK (length(lname) <= 128),
            username STRING (128) PRIMARY KEY NOT NULL CHECK (length(username) <= 128),
            password STRING (128) NOT NULL CHECK (length(password) <= 128)) ;''')
        Data.save()

    @staticmethod
    def insert_in_database(fname, lname, username, password):
        Data.exec(f'''insert into USER values
            ("{fname}", "{lname}", "{username}", "{password}") ;''')
        Data.save()
        del fname, lname, username, password

    ####################################################################################################################

    @staticmethod
    def create_logger():
        Data.exec('''CREATE TABLE IF NOT EXISTS LOGIN (
            user STRING  CHECK (length(user) <= 128)) ;''')
        Data.save()

    @staticmethod
    def keep_logged_in(user):
        Data.open()
        Data.exec(f''' insert into LOGIN values("{user}") ;''')
        Data.save()
        Data.close()
        del user

    @staticmethod
    def check_logged_in():
        Data.open()
        try:
            Data.exec("select * from LOGIN ;")
            data = Data.getone()
        except:
            return None, False
        else:
            if data:
                return data[0], True
            else:
                return None, False
        finally:
            Data.close()

    @staticmethod
    def not_logged_in():
        Data.open()
        Data.exec("delete from LOGIN ;")
        Data.save()
        Data.close()

    ####################################################################################################################

    @staticmethod
    def create_user(name):
        Data.exec(f'''CREATE TABLE "{name}"
        (field STRING (128) NOT NULL CHECK (length(field) <= 128),
        data STRING (256) NOT NULL CHECK (length(data) <= 256),
        password STRING (256) NOT NULL CHECK (length(password) <= 256),
        desc STRING (256) NOT NULL CHECK (length(desc) <= 256)) ;''')
        Data.save()
        del name

    @staticmethod
    def insert_in_user(name, data):
        Data.exec(f'''insert into "{name}" values
                    ("{data[0]}", "{data[1]}", "{data[2]}", "{data[3]}") ;''')
        Data.save()
        del name, data

    @staticmethod
    def update_user_pass(user, pid, data):
        Data.exec(f'''update "{user}" set field = "{data[0]}" ,
                    data = "{data[1]}" , password = "{data[2]}" ,
                     desc = "{data[3]}"  where  rowid = "{pid}" ''')
        Data.save()
        del user, pid, data

    ####################################################################################################################

    @staticmethod
    def get_key():
        key = ""
        for i in range(128):
            key += choice("0123456789abcdef")
        return key

    @staticmethod
    def get_hash(text):
        text = text
        for i in range(1024):
            text = text.encode("ascii")
            text = sha3_512(text).hexdigest()
        return text

    @staticmethod
    def find_key(user):
        Data.exec(f'''select fname from USER where username = "{user}" ;''')
        key = Data.getone()
        key = key[0]
        key = b64encode(key[::4].encode("ascii"))
        return key

    @staticmethod
    def encrypt_one_pass(key, data):
        fernet = Fernet(key)
        tup = ((fernet.encrypt(data[0].encode("ascii"))).decode(),
               (fernet.encrypt(data[1].encode("ascii"))).decode(),
               (fernet.encrypt(data[2].encode("ascii"))).decode(),
               (fernet.encrypt(data[3].encode("ascii"))).decode())
        del fernet, data
        return tup

    @staticmethod
    def decrypt_one_pass(user, data):
        key = Data.find_key(user)
        fernet = Fernet(key)
        tup = ((fernet.decrypt(data[0].encode("ascii"))).decode(),
               (fernet.decrypt(data[1].encode("ascii"))).decode(),
               (fernet.decrypt(data[2].encode("ascii"))).decode(),
               (fernet.decrypt(data[3].encode("ascii"))).decode())
        del user, data, key, fernet
        return tup

    @staticmethod
    def decrypt_all_pass(user):
        key = Data.find_key(user)
        fernet = Fernet(key)
        Data.exec(f''' select rowid,* from "{user}" ;''')
        orig = Data.getall()
        new = []
        for i in orig:
            new.append((i[0], (fernet.decrypt(i[1].encode("ascii"))).decode(),
                        (fernet.decrypt(i[2].encode("ascii"))).decode(),
                        (fernet.decrypt(i[3].encode("ascii"))).decode(),
                        (fernet.decrypt(i[4].encode("ascii"))).decode()))
        del orig, key, fernet
        return new

    ####################################################################################################################

    @staticmethod
    def createram():
        Data.exec('CREATE TABLE IF NOT EXISTS RAM ( value text) ; ')
        Data.save()

    @staticmethod
    def savetoram(*args):
        Data.open()
        for data in args:
            Data.exec(f'''insert into RAM values ("{data}")''')
        Data.save()
        Data.close()
        del args

    @staticmethod
    def getfromram():
        Data.open()
        Data.exec('select * from RAM ;')
        data = Data.getall()
        Data.close()
        return data

    @staticmethod
    def delfromram():
        Data.exec('delete from RAM ;')
        Data.save()

    ####################################################################################################################

    @staticmethod
    def register_user(name, username, password):
        Data.open()
        fname = Data.get_key()
        name = Data.get_hash(name)
        username = Data.get_hash(username)
        password = Data.get_hash(password)

        try:
            Data.insert_in_database(fname, name, username, password)
            Data.create_user(username)
        except:
            return False
        else:
            Data.save()
            return True
        finally:
            Data.close()
            del name, fname, username, password

    ####################################################################################################################

    @staticmethod
    def login_user(user, passwd):
        user = Data.get_hash(user)
        passwd = Data.get_hash(passwd)
        Data.open()

        try:
            Data.exec(f'''select username from USER where username = "{user}" ;''')
            stat1 = Data.getone()
        except:
            pass
        else:
            Data.exec(f'''select username,password from USER
                where username = "{user}" and
                password = "{passwd}" ;''')
            stat2 = Data.getone()
            return stat1, stat2, user
        finally:
            Data.close()
            del user, passwd, stat1, stat2

    ####################################################################################################################

    @staticmethod
    def save_password(user, data):
        Data.open()
        key = Data.find_key(user)
        data = Data.encrypt_one_pass(key, data)

        try:
            Data.insert_in_user(user, data)
        except:
            return 0
        else:
            Data.exec(f'''select max(rowid) from "{user}" ;''')
            Data.save()
            return Data.getone()[0]
        finally:
            Data.close()
            del user, data, key

    ####################################################################################################################

    @staticmethod
    def view_all_password(user):
        Data.open()

        try:
            return Data.decrypt_all_pass(user)
        except:
            pass
        finally:
            Data.close()
            del user

    ####################################################################################################################

    @staticmethod
    def pre_edit_password(user, pid):
        Data.open()

        try:
            Data.exec(f''' select * from "{user}" where rowid = "{pid}" ;''')
        except:
            return None
        else:
            data = Data.getone()
            return Data.decrypt_one_pass(user, data) if data else None
        finally:
            Data.close()
            del user, pid, data

    ####################################################################################################################

    @staticmethod
    def edit_password(user, pid, data):
        Data.open()
        key = Data.find_key(user)
        data = Data.encrypt_one_pass(key, data)

        try:
            Data.update_user_pass(user, pid, data)
        except:
            return False
        else:
            return True
        finally:
            Data.close()
            del user, pid, data, key

    ####################################################################################################################

    @staticmethod
    def delete_password(user, pid):
        Data.open()

        try:
            Data.exec(f''' delete from "{user}" where  rowid = "{pid}" ;''')
        except:
            return False
        else:
            Data.save()
            return True
        finally:
            Data.close()
            del user, pid

    ####################################################################################################################

    @staticmethod
    def delete_user(user):
        Data.open()
        try:
            Data.exec(f'''drop table "{user}" ;''')
            Data.exec(f''' delete from USER where username = "{user}" ;''')
            Data.exec("delete from LOGIN ;")
        except:
            return False
        else:
            Data.save()
            return True
        finally:
            Data.close()

    ####################################################################################################################

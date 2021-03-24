from kivy.lang.builder import Builder
from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty, ListProperty, StringProperty
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.config import Config
from kivy.core.window import Window

from kivymd.app import MDApp
from kivymd.toast import toast
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton, MDFillRoundFlatIconButton
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.datatables import MDDataTable

from random import shuffle
from ast import literal_eval as leval

from Data_Handler import *

lenpass = None
coming_from_gen = False
user_logged_in, login_status = Data.check_logged_in()
coming_from_mgr = False
pid = None

Config.set('kivy', 'exit_on_escape', '0')
Config.set('kivy', 'pause_on_minimize', '1')


########################################################################################################################


class Show:
    @staticmethod
    def dialog(title, text):
        dialog = MDDialog(title=title, text=text,
                          buttons=[MDFillRoundFlatIconButton(
                              text="Dismiss", icon="close",
                              on_release=lambda x: dialog.dismiss())])
        dialog.open()

    @staticmethod
    def snack(text):
        snack = Snackbar(text=text, font_size=20)
        snack.open()

    @staticmethod
    def toast(text):
        toast(text)

    @staticmethod
    def dialogbtn(title, btn1, btn2, btn2act):
        dialog = MDDialog(title=title, type="simple",
                          buttons=[MDRaisedButton(
                              text=btn1,
                              on_release=lambda x: dialog.dismiss()),
                              MDRaisedButton(
                                  text=btn2,
                                  on_release=lambda x: btn2act(),
                                  on_press=lambda x: dialog.dismiss())])
        dialog.open()


########################################################################################################################


class Mainapp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.screen = Builder.load_file("design.kv")
        self.old = StringProperty()

    def on_start(self):
        Data.open_close(Data.create_database,
                        Data.createram,
                        Data.create_logger,
                        Data.delfromram)
        Clock.schedule_interval(self.update_label, 1)

    def on_stop(self):
        Data.open_close(Data.delfromram)

    def build(self):
        Window.bind(on_key_down=self.key_action)
        self.theme_cls.primary_palette = "Teal"
        self.theme_cls.theme_style = "Dark"
        self.title = "Password Generator"
        self.icon = "ss.ico"
        return self.screen

    def key_action(self, *args):
        if args[1] == 27 or args[1] == 1001:
            self.back()

    @staticmethod
    def loggedin():
        if login_status:
            return True
        else:
            return False

    def logout(self):
        global login_status, user_logged_in
        login_status, user_logged_in = False, None
        Data.not_logged_in()
        screen = self.screen.ids.scr_mgr.current

        if screen != "scr_gen":
            self.screen.ids.scr_mgr.current = "scr_login"
            self.screen.ids.toolbar.title = "LOGIN"

    def update_label(self, *args):
        current = self.screen.ids.scr_mgr.current
        if self.old != current:
            if current == "scr_reg":
                self.screen.ids.toolbar.title = "REGISTER"
            elif current == "scr_login":
                self.screen.ids.toolbar.title = "LOGIN"
            elif current == "scr_manager":
                self.screen.ids.toolbar.title = "MANAGER"
            elif current == "scr_viewall":
                self.screen.ids.toolbar.title = "VIEW ALL"
            elif current == "scr_predit":
                self.screen.ids.toolbar.title = "EDIT PASSWORD"
            elif current == "scr_edit":
                self.screen.ids.toolbar.title = "EDIT PASSWORD"
            elif current == "scr_svinfo":
                self.screen.ids.toolbar.title = "SAVE PASSWORD"
            elif current == "scr_gen":
                self.screen.ids.toolbar.title = "GENERATOR"
        self.old = current

    def back(self):
        current = self.screen.ids.scr_mgr.current
        if current == "scr_reg":
            self.screen.ids.scr_mgr.current = "scr_login"
            self.screen.ids.toolbar.title = "LOGIN"
            self.screen.ids.scr_mgr.transition.direction = 'left'
        elif current == "scr_login":
            self.screen.ids.scr_mgr.current = "scr_gen"
            self.screen.ids.toolbar.title = "GENERATOR"
            self.screen.ids.scr_mgr.transition.direction = 'down'
        elif current == "scr_manager":
            self.screen.ids.scr_mgr.current = "scr_gen"
            self.screen.ids.toolbar.title = "GENERATOR"
            self.screen.ids.scr_mgr.transition.direction = 'down'
        elif current == "scr_viewall":
            self.screen.ids.scr_mgr.current = "scr_manager"
            self.screen.ids.toolbar.title = "MANAGER"
            self.screen.ids.scr_mgr.transition.direction = 'right'
        elif current == "scr_predit":
            self.screen.ids.scr_mgr.current = "scr_manager"
            self.screen.ids.toolbar.title = "MANAGER"
            self.screen.ids.scr_mgr.transition.direction = 'right'
        elif current == "scr_edit":
            self.screen.ids.scr_mgr.current = "scr_predit"
            self.screen.ids.toolbar.title = "PREDIT PASSWORD"
            self.screen.ids.scr_mgr.transition.direction = 'right'
        elif current == "scr_svinfo":
            global coming_from_mgr
            if coming_from_mgr:
                self.screen.ids.scr_mgr.current = "scr_manager"
                self.screen.ids.scr_mgr.transition.direction = 'right'
                self.screen.ids.toolbar.title = "MANAGER"
                coming_from_mgr = False
            else:
                self.screen.ids.scr_mgr.current = "scr_gen"
                self.screen.ids.scr_mgr.transition.direction = 'down'
                self.screen.ids.toolbar.title = "GENERATOR"
        elif current == "scr_gen":
            Show.dialogbtn("Do you want to EXIT?", "NO", "YES", self.get_running_app().stop)

    ####################################################################################################################

    class Generator(Screen):
        special_char = ("_", "@", "#")  # Special_Characters

        capital_char = (
            "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O",
            "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z")  # Capital_Letters

        number_char = ("0", "1", "2", "3", "4", "5", "6", "7", "8", "9")  # Numbers

        small_char = ("a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o",
                      "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z")  # Small_Letters

        genlenbox = ObjectProperty(None)
        genchkspe = ObjectProperty(None)
        genchkcap = ObjectProperty(None)
        genchknum = ObjectProperty(None)
        genchksml = ObjectProperty(None)
        genpassbox = ObjectProperty(None)

        @staticmethod
        def loggedin():
            if login_status:
                return True
            else:
                return False

        # Copy Item to ClipBoard
        def copy_password(self):
            self.genpassbox.copy(data=self.genpassbox.text)

        # go to save for saving password
        def save_pwd(self):
            global coming_from_gen
            Data.savetoram(self.genpassbox.text)
            self.genpassbox.text = ''
            coming_from_gen = True

        # Generate Password
        @staticmethod
        def generate(lenpasswd, chardict):
            password = ''
            for i in range(lenpasswd):
                password += choice(chardict)
            return password

        # Display The Password
        def show(self):
            global lenpass
            self.genpassbox.readonly = False
            self.genpassbox.text = ""
            password = self.generate(lenpass, self.make_list())
            self.genpassbox.text = password
            self.genpassbox.readonly = True

        # Collect Status of checkbox
        def get_status(self):
            chk1stat = self.genchkspe.active
            chk2stat = self.genchkcap.active
            chk3stat = self.genchknum.active
            chk4stat = self.genchksml.active
            return chk1stat, chk2stat, chk3stat, chk4stat

        # Check Condition
        def condition(self):
            global lenpass
            lenpass = int(self.genlenbox.text)

            chk1stat, chk2stat, chk3stat, chk4stat = self.get_status()

            if chk1stat or chk2stat or chk3stat or chk4stat:
                self.show()
            else:
                Show.toast("Select a minimum of one Checkbox!")
            del chk1stat, chk2stat, chk3stat, chk4stat

        # makes dictionary of character
        def make_list(self):
            chk1stat, chk2stat, chk3stat, chk4stat = self.get_status()

            tup = ()

            if chk1stat or chk2stat or chk3stat or chk4stat:
                if chk1stat:
                    if chk2stat:
                        if chk3stat:
                            if chk4stat:
                                tup = self.special_char + self.capital_char + self.number_char + self.small_char
                            else:
                                tup = self.special_char + self.capital_char + self.number_char
                        else:
                            if chk4stat:
                                tup = self.special_char + self.capital_char + self.small_char
                            else:
                                tup = self.special_char + self.capital_char
                    else:
                        if chk3stat:
                            if chk4stat:
                                tup = self.special_char + self.number_char + self.small_char
                            else:
                                tup = self.special_char + self.number_char
                        else:
                            if chk4stat:
                                tup = self.special_char + self.small_char
                            else:
                                tup = self.special_char
                else:
                    if chk2stat:
                        if chk3stat:
                            if chk4stat:
                                tup = self.capital_char + self.number_char + self.small_char
                            else:
                                tup = self.capital_char + self.number_char
                        else:
                            if chk4stat:
                                tup = self.capital_char + self.small_char
                            else:
                                tup = self.capital_char
                    else:
                        if chk3stat:
                            if chk4stat:
                                tup = self.number_char + self.small_char
                            else:
                                tup = self.number_char
                        else:
                            if chk4stat:
                                tup = self.small_char

            del chk1stat, chk2stat, chk3stat, chk4stat
            return self.shuffler(tup)

        # shuffles the characters
        @staticmethod
        def shuffler(tup):
            charlist = list(tup)
            shuffle(charlist)
            return tuple(charlist)

    ####################################################################################################################

    class Register_user(Screen):
        regfname = ObjectProperty(None)
        reglname = ObjectProperty(None)
        reguser = ObjectProperty(None)
        regpass1 = ObjectProperty(None)
        regpass2 = ObjectProperty(None)

        def on_leave(self, *args):
            self.regfname.text = self.reglname.text = self.reguser.text = self.regpass1.text = self.regpass2.text = ''

        # Registers the user
        def registering_user(self):
            fname = self.regfname.text.lower().strip()
            lname = self.reglname.text.lower().strip()
            username = self.reguser.text.lower().strip()
            password = self.regpass1.text.strip()
            password2 = self.regpass2.text.strip()

            if password == password2:
                if Data.register_user(fname + " " + lname, username, password):
                    Show.dialog("Congratulations", "Account Created Successfully")
                    self.manager.current = "scr_login"
                    self.manager.transition.direction = 'left'
                else:
                    Show.toast("User Already Exist!!")
            else:
                Show.toast("Password Not Matching!!")
                self.regpass1.text = self.regpass2.text = ''

            del fname, lname, username, password, password2

    ####################################################################################################################

    class Login_user(Screen):
        loginuser = ObjectProperty(None)
        loginpass = ObjectProperty(None)
        logincheck = ObjectProperty(None)

        @staticmethod
        def loggedin():
            if login_status:
                return True
            else:
                return False

        def on_leave(self, *args):
            self.loginuser.text = self.loginpass.text = ''
            self.logincheck.active = False

        # gives location to go after login
        def going_to(self):
            global coming_from_gen
            stat = self.loggedin()

            if coming_from_gen and stat:
                self.manager.current = "scr_svinfo"
                self.manager.transition.direction = 'left'
            elif stat:
                self.manager.current = "scr_manager"
                coming_from_gen = False
                self.manager.transition.direction = 'left'
            del stat

        # Logs in the user
        def logging_in_user(self):
            global login_status, user_logged_in

            username = self.loginuser.text.lower().strip()
            password = self.loginpass.text.strip()

            userstat, loginstat, user = Data.login_user(username, password)
            if username and password:
                if userstat:
                    if loginstat:
                        Show.dialog("Congratulations", 'Logged in successfully')
                        login_status = True
                        user_logged_in = user
                        if self.logincheck.active:
                            Data.keep_logged_in(user)
                        self.going_to()
                    else:
                        Show.toast('User Credentials not Matching!')
                else:
                    Show.toast('User not Found !! \n Please Register')
            else:
                if len(password):
                    Show.toast('Username cannot be blank!!')
                elif len(username):
                    Show.toast('Password cannot be blank!!')
                else:
                    Show.toast('Fill in the User Credentials!!')

            del username, password, userstat, loginstat, user

    ####################################################################################################################

    class Manage(Screen):
        @staticmethod
        def going_to_save():
            global coming_from_mgr
            coming_from_mgr = True

        # delete the user prequel
        def del_user(self):
            Show.dialogbtn("Do you want to Delete your Account ?", "No", "Yes", self.deleting_user)

        # Deleting the user
        def deleting_user(self):
            global user_logged_in, login_status, coming_from_gen, coming_from_mgr

            if Data.delete_user(user_logged_in):
                user_logged_in = None
                login_status = coming_from_gen = coming_from_mgr = False
                self.manager.current = "scr_login"
                self.manager.transition.direction = 'right'
                Show.dialog("Information", "Account Successfully Deleted !")

            else:
                Show.toast("Account not Deleted ")

    ####################################################################################################################

    class Saveuserdata(Screen):

        svfield = ObjectProperty(None)
        svdata = ObjectProperty(None)
        svpass = ObjectProperty(None)
        svdesc = ObjectProperty(None)

        # saving password from generator
        def saving_genpass(self):
            global coming_from_gen
            if coming_from_gen:
                data = Data.getfromram()
                self.svpass.text = data[0][0]
                self.svpass.hint_text = "Password"
                coming_from_gen = False
                Data.open_close(Data.delfromram)
                del data

        def on_pre_enter(self):
            self.saving_genpass()

        def on_leave(self, *args):
            self.svdata.text = self.svpass.text = self.svdesc.text = ''
            self.svfield.text = "Username"

        @staticmethod
        def going_back():
            global coming_from_mgr
            if coming_from_mgr:
                coming_from_mgr = False

        def check_data(self, field, data):
            if (field == "Email") and ("@" not in data):
                self.svdata.text = ""
                Show.toast("Enter Valid Email")
                return False
            elif (field == "Site") and ("." not in data):
                self.svdata.text = ""
                Show.toast("Enter Valid Site")
                return False
            else:
                return True

        # Saving password
        def saving_password(self):
            global user_logged_in

            field = self.svfield.text
            data = self.svdata.text.strip()
            password = self.svpass.text.strip()
            desc = self.svdesc.text.strip()

            if len(data) and len(password):
                if self.check_data(field, data):
                    num = Data.save_password(user_logged_in, (field, data, password, desc))
                    if num > 0:
                        Show.dialog("Congratulations !",
                                    f'Password Saved Successfully !\n \n Your PID for this password is  {num} ')
                        self.manager.current = 'scr_manager'
                        self.manager.transition.direction = 'right'
                    else:
                        Show.dialog("Error !!", "Password not Saved ")
                    del num
            else:
                if len(password):
                    Show.toast(f"Data in {field} should not be Null ")
                else:
                    Show.toast("Length of Password should not be Null ")

            del field, data, password, desc

    ####################################################################################################################

    class Viewall(Screen):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.data = ListProperty()
            self.table = ObjectProperty(None)
            self.data_old = ListProperty()

        layout = ObjectProperty(None)
        srchbox = ObjectProperty(None)
        srchdata = ObjectProperty(None)

        def show_table(self, data):
            self.table = MDDataTable(
                size_hint=(1, 0.85),
                pos_hint={"center_x": 0.5, "center_y": 0.425},
                elevation=0,
                rows_num=100000,
                column_data=[
                    ("PID", dp(10)),
                    ("FIELD", dp(20)),
                    ("DATA", dp(40)),
                    ("PASSWORD", dp(40)),
                    ("DESCRIPTION", dp(40))],
                row_data=data)

            self.layout.add_widget(self.table)

        def on_pre_enter(self, *args):
            global user_logged_in
            self.data = Data.view_all_password(user_logged_in)

        def on_enter(self, *args):
            self.normal()

        def normal(self):
            if self.data:
                self.show_table(self.data)
            else:
                Show.dialog("Error", "No Data was found")

        def search(self):
            col = self.srchbox.text
            data = self.srchdata.text.strip()

            self.layout.remove_widget(self.table)

            new = []

            for i in self.data:
                if col == "All":
                    new = self.data
                    self.srchdata.text = ""
                elif (i[1] == col) and (data in i[2]):
                    new.append(i)
            if new:
                self.show_table(new)
                del new
            else:
                Show.dialog("Error", "No Data was found")

    ####################################################################################################################

    class Predit(Screen):
        predpid = ObjectProperty(None)

        def on_leave(self, *args):
            self.predpid.text = ''

        # gets data for the password id
        def predpass(self):
            global user_logged_in, pid

            pid = self.predpid.text.strip()

            data = Data.pre_edit_password(user_logged_in, pid)

            if data:
                Data.savetoram(pid, data)
                self.manager.current = 'scr_edit'
                self.manager.transition.direction = 'left'
            else:
                Show.toast("PID not Available !")
                self.predpid.text = ''

            del data

    ####################################################################################################################

    class Edit(Screen):
        edfield = ObjectProperty(None)
        eddata = ObjectProperty(None)
        edpass = ObjectProperty(None)
        eddesc = ObjectProperty(None)

        @staticmethod
        def unpack():
            global pid
            packet = Data.getfromram()
            return int(packet[0][0]), leval(packet[1][0])

        def on_pre_enter(self, *args):
            global pid
            pid, data = self.unpack()

            self.edfield.text = data[0]
            self.eddata.text = data[1]
            self.eddata.hint_text = self.edfield.text
            self.edpass.text = data[2]
            self.eddesc.text = data[3]

            del data

        def on_leave(self, *args):
            Data.open_close(Data.delfromram)
            self.eddata.text = self.edpass.text = self.eddesc.text = ''
            self.edfield.text = "Username"

        # Edits the password
        def editingpass(self):
            global user_logged_in, pid

            field = self.edfield.text
            data = self.eddata.text.strip()
            password = self.edpass.text.strip()
            desc = self.eddesc.text.strip()

            if len(data) and len(password):
                if Data.edit_password(user_logged_in, pid, (field, data, password, desc)):
                    Show.toast('Password Updated Successfully !')
                    self.manager.current = 'scr_manager'
                    self.manager.transition.direction = 'right'
                else:
                    Show.toast("Password not Updated ")
            else:
                if len(password):
                    Show.toast(f"Data in {field} should not be Null ")
                else:
                    Show.toast("Length of Password should not be Null ")

            del field, data, password, desc

        # Delete password prequel
        def deletepass(self):
            Show.dialogbtn("Do you want to Delete this password ?", "No", "Yes", self.deletingpass, )

        # deleting password
        def deletingpass(self):
            global user_logged_in, pid

            if Data.delete_password(user_logged_in, pid):
                Show.toast("Password Successfully Deleted!!")
                self.manager.current = "scr_manager"
                self.manager.transition.direction = 'right'
            else:
                Show.toast("Password not Deleted!! ")

    ####################################################################################################################


if __name__ == "__main__":
    Mainapp().run()

from multiprocessing import Pool, Manager
from time import sleep
from wmi import WMI
from win32com.client import GetObject
from subprocess import Popen
from collections import Iterable
from tqdm import tqdm
from uuid import uuid4
from os import getpid, pathsep, remove, path
from tempfile import gettempdir

session_process = None
all_processes_id = []


def _on_init(sid, p_ids):
    p_ids.append(getpid())
    global session_process
    app = SAP.app()
    i = 0
    while True:
        con = app.Children(i)
        if con.Children(0).Info.systemsessionid == sid:
            session_process = con.Children(p_ids.index(getpid()))
            break
        i = i + 1


def _task_executor(task):
    task['func'](task['data'])


class SAP:

    def __init__(self, max_sessions=16):
        self._con = None
        self._tasks = []
        self.max_sessions = max_sessions
        self.session = lambda i=0: self._con.Children(i)
        self._connected = False

    @staticmethod
    def app():
        """Open SAPGui"""
        wmi_obj = WMI()

        sap_exists = len(wmi_obj.Win32_Process(name='saplgpad.exe')) > 0

        if not sap_exists:
            Popen(['C:\Program Files (x86)\SAP\FrontEnd\SAPgui\saplgpad.exe'])

        while True:
            try:
                return GetObject("SAPGUI").GetScriptingEngine
            except:
                sleep(1)
                pass


    def get_sbar_status(self, session):
        return session.findById("wnd[0]/sbar/pane[0]").text

    def window_caption(self, session):
        return session.ActiveWindow.Text

    def test_connection(self, session):
        """SAP connection test"""
        try:
            session.findById("wnd[0]/tbar[0]/okcd").text = "/n"
            session.findById("wnd[0]").sendVKey(0)
            session.findById("wnd[0]/usr/btnSTARTBUTTON").press()
            return True
        except:
            return False
            raise ValueError('SAP was not connected.')


    def connect(self, environment, client=None, user=None, password=None, lang=None, force=False):
        con = SAP.app().OpenConnection(environment, True)
        session = con.Children(0)

        if client is not None:
            session.findById("wnd[0]/usr/txtRSYST-MANDT").Text = client

        if user is not None:
            session.findById("wnd[0]/usr/txtRSYST-BNAME").Text = user

        if password is not None:
            session.findById("wnd[0]/usr/pwdRSYST-BCODE").Text = password

        if lang is not None:
            session.findById("wnd[0]/usr/txtRSYST-LANGU").Text = lang

        session.findById("wnd[0]").sendVKey(0)

        #Eventual tela de mudanca de senha
        change_pwd = False
        try:
            session.findById("wnd[1]/usr/pwdRSYST-NCODE").text = ''
            session.findById("wnd[1]/usr/pwdRSYST-NCOD2").text = ''
            change_pwd = True
        except:
            pass

        if change_pwd:
            raise ValueError('Please, set a new Password')

        # Derruba conexão SAP
        if force:
            try:
                session.findById("wnd[1]/usr/radMULTI_LOGON_OPT1").select()
                session.findById("wnd[1]/tbar[0]/btn[0]").press()
            except:
                pass
        else:
            try:
                session.findById("wnd[1]/usr/radMULTI_LOGON_OPT1").select()
                session.findById("wnd[1]").sendVKey(12)
                return False
            except:
                pass

        # Teste da Conexao
        if self.test_connection(session):
            self._connected = True

        del session
        self._con = con
        return self._connected

    @property
    def connected(self):
        return self._connected

    @staticmethod
    def session():
        global session_process
        return session_process

    def sid(self):
        return self.session().Info.systemsessionid

    def logout(self):
        session = self.session()
        session.findById("wnd[0]/tbar[0]/okcd").text = "/nex"
        session.findById("wnd[0]").sendVKey(0)
        del session
        self._con = None

    @property
    def number_of_sessions(self):
        return 0 if self._con is None else len(self._con.Children)

    @number_of_sessions.setter
    def number_of_sessions(self, value):
        size = self.number_of_sessions
        if size == 0:
            return

        value = min(max(int(value), 1), self.max_sessions)
        minus = value < size
        arr = list(range(size, value))
        arr.extend(reversed(range(value, size)))

        for i in arr:
            if minus:
                session = self.session(i)
                session.findById("wnd[0]/tbar[0]/okcd").text = "/i"
                session.findById("wnd[0]").sendVKey(0)
            else:
                self.session().createSession()
                sleep(0.5)

    def clear_tasks(self):
        self._tasks = []

    def add_task(self, func, data):
        for dt in data:
            self._tasks.append({'func': func, 'data': dt})

    def execute_tasks(self, resize_sessions=False):
        total = len(self._tasks)
        if total == 0:
            return

        if resize_sessions:
            self.number_of_sessions = total

        size = self.number_of_sessions

        if size == 0:
            return
        sess_manager = Manager().list([])

        pool = Pool(processes=self.number_of_sessions, initializer=_on_init, initargs=(self.sid(), sess_manager))
        response = list(tqdm(pool.imap_unordered(_task_executor, self._tasks)))
        pool.close()
        pool.join()
        return list(response)

    def execute_function(self, func, data, resize_sessions=False):
        if not isinstance(data, Iterable):
            data = [data]
        self.clear_tasks()
        self.add_task(func=func, data=data)
        response = self.execute_tasks(resize_sessions=resize_sessions)
        self.clear_tasks()
        return response

    @staticmethod
    def append_multi_selection(data):
        if type(data) is not str:
            data = "\r".join([str(d) for d in data])

        folder = gettempdir() + pathsep
        file_name = "temp_append_{}_{}.txt".format(uuid4().hex, str(getpid()))
        file_address = path.join(folder[:-1], file_name)
        with open(file_address, 'w+') as f:
            f.write(data)
        del f
        session = SAP.session()
        session.findById("wnd[1]/tbar[0]/btn[16]").press()
        session.findById("wnd[1]/tbar[0]/btn[23]").press()
        session.findById("wnd[2]/usr/ctxtDY_PATH").text = folder[:-1]
        session.findById("wnd[2]/usr/ctxtDY_FILENAME").text = file_name
        session.findById("wnd[2]").sendVKey(0)
        session.findById("wnd[1]").sendVKey(8)
        remove(file_address)

    @staticmethod
    def multi_arguments(func):
        def convert_args(pr):
            return func(**pr)

        return convert_args

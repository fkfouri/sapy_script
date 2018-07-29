from inspect import ismethod
from uuid import uuid4
from os import getpid, remove, path
from tempfile import gettempdir


class Session:
    def __init__(self, session):
        self._session = session

    def __getattr__(self, attr):
        attr = getattr(self._session, attr)
        if ismethod(attr):
            def wrapper(*args, **kw):
                return attr(*args, **kw)

            return wrapper

        return attr

    def append_multi_selection(self, data):
        if type(data) is not str:
            data = "\r".join([str(d) for d in data])
        folder = gettempdir().rstrip(';')
        file_name = "temp_append_{}_{}.txt".format(uuid4().hex, str(getpid()))
        file_address = path.join(folder, file_name)
        with open(file_address, 'w+') as f:
            f.write(data)
        del f
        session = self._session
        session.findById("wnd[1]/tbar[0]/btn[16]").press()
        session.findById("wnd[1]/tbar[0]/btn[23]").press()
        session.findById("wnd[2]/usr/ctxtDY_PATH").text = folder[:-1]
        session.findById("wnd[2]/usr/ctxtDY_FILENAME").text = file_name
        session.findById("wnd[2]").sendVKey(0)
        session.findById("wnd[1]").sendVKey(8)
        remove(file_address)

    def get_sbar_status(self):
        return self._session.findById("wnd[0]/sbar/pane[0]").text

    def window_caption(self):
        return self._session.ActiveWindow.Text

    def is_connected(self):
        """SAP connection test"""
        try:
            session = self._session
            session.findById("wnd[0]/tbar[0]/okcd").text = "/n"
            session.findById("wnd[0]").sendVKey(0)
            session.findById("wnd[0]/usr/btnSTARTBUTTON").press()
            return True
        except:
            raise ValueError('SAP was not connected.')
            return False

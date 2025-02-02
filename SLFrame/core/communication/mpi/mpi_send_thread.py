import ctypes
import logging
import threading
import time
import traceback
import sys
from ..message import Message


class MPISendThread(threading.Thread):
    def __init__(self, comm, rank, size, name, q):
        super(MPISendThread, self).__init__()
        self._stop_event = threading.Event()
        self.comm = comm
        self.rank = rank
        self.size = size
        self.name = name
        self.q = q
        self.total_send_size = 0
        self.tmp_send_size = 0

    def run(self):
        logging.info("Starting " + self.name + ". Process ID = " + str(self.rank))
        while True:
            try:
                if not self.q.empty():
                    msg = self.q.get()
                    msg_str = msg.to_string()
                    size = msg.get_size()
                    self.tmp_send_size += size
                    self.total_send_size += size
                    dest_id = msg.get(Message.MSG_ARG_KEY_RECEIVER)
                    self.comm.send(msg_str, dest=dest_id)
                else:
                    time.sleep(0.03)
            except Exception:
                traceback.print_exc()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

    def get_id(self):
        # returns id of the respective thread
        if hasattr(self, '_thread_id'):
            return self._thread_id
        for id, thread in threading._active.items():
            if thread is self:
                return id

    def raise_exception(self):
        thread_id = self.get_id()
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id,
                                                         ctypes.py_object(SystemExit))
        if res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
            print('Exception raise failure')

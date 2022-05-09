from mpi4py import MPI
import random
import torch
import logging
import numpy as np
from .message_define import MyMessage
from ...communication.msg_manager import MessageManager
from ...communication.message import Message
from ...log.Log import Log



class ServerManager(MessageManager):

    def __init__(self, args, trainer, backend="MPI"):
        super().__init__(args, "server", args["comm"], args["rank"],
                         args["max_rank"] + 1, backend)
        self.log = Log(self.__class__.__name__, args)
        self.trainer = trainer
        self.active_node = -1
        self.batch_size = args["batch_size"]
        self.finished_nodes = 0
        self.client_num = args["max_rank"]
        self.acts_buffer= {}
        self.counter=0
        # logging.warning("server rank{} args{}".format(self.rank,args["rank"]))

    def run(self):
        super().run()

    def send_grads_to_client(self, receive_id, grads=None):
        message = Message(MyMessage.MSG_TYPE_S2C_GRADS, self.rank, receive_id)
        message.add_params(MyMessage.MSG_ARG_KEY_GRADS, grads)
        message.add_params(MyMessage.MSG_AGR_KEY_RESULT, (self.trainer.total, self.trainer.correct, self.trainer.val_loss,self.trainer.predict))
        self.send_message(message)

    def register_message_receive_handlers(self):
        self.register_message_receive_handler(MyMessage.MSG_TYPE_C2S_SEND_ACTS,
                                              self.handle_message_acts)
        self.register_message_receive_handler(MyMessage.MSG_TYPE_C2S_PROTOCOL_FINISHED,
                                              self.handle_message_finish_protocol)

    def handle_message_acts(self, msg_params):
        acts, labels = msg_params.get(MyMessage.MSG_ARG_KEY_ACTS)
        self.active_node = msg_params.get(MyMessage.MSG_ARG_KEY_SENDER)
        client_phase = msg_params.get(MyMessage.MSG_ARG_KEY_PHASE)
        if client_phase == "train":
            self.counter += 1
            self.acts_buffer[self.active_node]=(acts,labels)
            if self.counter == self.client_num:
                self.counter = 0
                tmp = self.shuffle_acts()
                for i in range(self.client_num):
                    self.trainer.train_mode()
                    acts,labels = tmp[i]
                    self.trainer.forward_pass(acts, labels)
                    grads = self.trainer.backward_pass()
                    self.send_grads_to_client(i+1, grads)
        else:
            self.trainer.eval_mode()
            self.trainer.forward_pass(acts, labels)
            self.send_grads_to_client(self.active_node)

    def shuffle_acts(self):
        lst = []
        all_acts = []
        all_labels = []
        res = []
        for v in self.acts_buffer.values():
            acts, labels = v
            all_acts.append(acts)
            all_labels.append(labels)

        all_acts = torch.cat(all_acts,dim=0)
        all_labels = torch.cat(all_labels,dim=0)
        for i in range(self.client_num):
            for j in range(self.batch_size):
                lst.append(i)

        random.shuffle(lst)
        lst=np.array(lst)
        for i in range(self.client_num):
            idx = np.where(lst == i)
            res.append((all_acts[idx, ][0],all_labels[idx, ][0]))

        return res




    def handle_message_finish_protocol(self):
        self.finished_nodes += 1
        if self.finished_nodes == self.trainer.MAX_RANK:
            self.finish()

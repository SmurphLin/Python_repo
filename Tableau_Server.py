import os
import sys
import tableauserverclient as TSC
import Lib
import numpy as np

def f():
    """login file"""
    f = "C:\\Users\\wmurphy\\Desktop\\PyProj\\creds.txt"
    return f



class TableauServer(object):
    """
    class:
        TableauServer
        -------------
        -base class that initializes
        all aspects of the Tableau Server administration
        -login/logout of the tableau server
        -retrieve information about project folders, workbooks, etc.
    """

    def __init__(self):
        self.creds_dict = None
        self.signed_in = False
        self.projects = None
        self.workbooks = None
        self.users = None

    def get_server_creds(self, f_path):
        """get server credentials and login
        to tableau server"""

        def inner_func():
            try:
                if os.path.isfile(f_path):
                    with open(f_path, "r") as file:
                        temp = np.array([f for f in file.read().splitlines()])
                    return temp
                else:
                    raise FileExistsError("Err[file not found]\n")
            except FileExistsError as fe:
                return fe
        inner = inner_func()
        self.creds_dict = {"authentication": TSC.TableauAuth(inner[0],
                                                             inner[1]),
                           "server": TSC.Server(inner[2])}

    def login(self):
        """login to tableau server"""
        if self.creds_dict is not None:
            try:
                if isinstance(self.creds_dict.get("server").auth.sign_in(self.creds_dict.get("authentication")),
                              TSC.server.endpoint.auth_endpoint.Auth.contextmgr):
                    self.creds_dict.get("server").auth.sign_in(self.creds_dict.get("authentication"))
                    self.signed_in = True
                else:
                    raise TSC.ServerResponseError("Err[could not login]\n")
            except TSC.ServerResponseError as tse:
                return tse
            except Exception("Unknown exception was raised '\n") as e:
                return e
        else:
            print("Server credentials not set\n")

    def logout(self):
        """logout of tableau server"""
        if self.signed_in is True and self.creds_dict is not None:
            self.creds_dict.get("server").auth.sign_out()
            self.signed_in = False
        else:
            print("Not signed into the server.\n")

    def get_projects(self):
        """get project files"""
        projects, pagination = self.creds_dict.get("server").projects.get()
        self.projects = {p.name: p.id for p in projects}

    def get_workbooks(self):
        """get workbook files"""
        workbooks, pagination = self.creds_dict.get("server").workbooks.get()
        self.workbooks = {w.name: w.id for w in workbooks}
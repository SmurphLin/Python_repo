import os
import sys
import numpy as np
import tableauserverclient as TSC
import zlib
import zipfile
import xml.etree.ElementTree


def f():
    """login file"""
    f = "C:\\Users\\wmurphy\\Desktop\\PyProj\\creds.txt"
    return f

class Node():
    """node class for xml tree traversing"""

    def __init__(self):
        """init"""
        self.head = None
        self.current = None
        self.next = None

    def set_node(self, value):
        """set th value of the node"""
        if self.head is None:
            self.head = value
            self.current = self.head

    def get_next(self, value):
        """set the value of the next node"""







class TableauServer(object):
    """login to tableau server"""

    def __init__(self):
        """
        parameters:
        -----------
            creds_dict: dictionary
                -holds tableau authorization
                and tableau server
            signed_in: boolean
                -true if logged into the tableau server,
                false otherwise
        """
        self.creds_dict = None
        self.signed_in = False

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


class Workbook(TableauServer):
    """Workbook class"""

    SESSION_WORKBOOKS = []

    def session_log(cls):
        """class method that keeps track
        of updates to workbooks during the session """

    def __init__(self):
        """init"""
        self.workbooks = None
        self.current_workbook = None
        self.is_twb_file = False
        super().__init__()

    def get_workbooks(self):
        """select the workbook
            :returns
                dict workbook id:name
        """
        if self.creds_dict is None:
            self.get_server_creds(f())
            print("getting server credentials ...\n")
        assert (isinstance(self.creds_dict.get("server").auth.sign_in(self.creds_dict.get("authentication")),
                           TSC.server.endpoint.auth_endpoint.Auth.contextmgr)), \
            "Err[error logging on to the server," \
            " check username and logon information]"

        if self.signed_in is False:
            self.login()
            print("logging in ...\n")

        self.creds_dict.get("server").auth.sign_in(self.creds_dict.get("authentication"))
        workbooks, pagination = self.creds_dict.get("server").workbooks.get()
        self.workbooks = {w.name: w.id for w in workbooks}

    def download_workbook(self, dl_path, wb_name):
        """download workbook of interest"""

        # set the path for the workbook to be downloaded
        try:
            if os.path.exists(dl_path):
                pass
            else:
                raise OSError("path not found\n")
        except OSError as oe:
            print(oe)
        except Exception:
            print("uncaught path exception was raised\n")

        # search for workbook id on the Tableau server
        try:
            if wb_name not in self.workbooks.keys():
                raise ValueError("workbook not found\n")
            else:
                wb_id = self.workbooks.get(wb_name)
                try:
                    wb_file = self.creds_dict.get("server").workbooks.download(wb_id, dl_path)
                except ValueError:
                    print("workbook could not be downloaded\n")
        except ValueError as ve:
            print(ve)
        except Exception:
            print("uncaught workbook exception was raised\n")
        finally:
            print("exiting download process ...\n")

    def open_workbook_xml(self, f_path, wb_name):
        """convert workbook to xml to enable
        editing to the xml tree"""
        try:
            if os.path.exists(f_path):
                try:
                    if os.path.isfile(f_path+'\\'+wb_name):
                        self.current_workbook = f_path+'\\'+wb_name
                        if self.current_workbook.split('.')[1] == 'twb':
                            self.is_twb_file = True
                        else:
                            temp_twb_file = self.current_workbook.split('.')[0]
                            # make current workbook a zipfile
                            zipped_wb = zipfile.ZipFile(self.current_workbook)
                            # extract all zipped file contents(gives us the .twb file)
                            zipped_wb.extractall(path=f_path)
                            print("unzipping workbook ... \n")
                            # close the .twbx file so we cna remove it
                            zipped_wb.close()
                            print("closing .twb file ...\n")
                            # remove the .twbx file
                            os.remove(f_path+'\\'+wb_name)
                            print("deleting .twbx file ... \n")
                            self.current_workbook = temp_twb_file+'.twb'
                    else:
                        raise FileNotFoundError("Err[file could nto be located\n]")
                except FileNotFoundError as fe:
                    print(fe)
            else:
                raise OSError("path not found\n")
        except OSError as pe:
            print(pe)
        finally:
            print("exiting workbook xml process ...\n")

    def update_workbook_parameter(self, parameter_name, dtype=None):
        """search for a parameter in the tableau
        workbook's xml framework"""
        # create an instance of the Node class
        self.current_workbook = xml.etree.ElementTree.parse(self.current_workbook)
        node = Node()
        node.set_node(value=self.current_workbook.getroot())
        root = node.head
        current = node.current
        print("root| {}".format(root))
        print("current| {}".format(current))
        this_param = "'[{}]'".format(parameter_name)
        re_xml_search = ".//*[@name={}]/members".format(this_param)
        print(root.find(re_xml_search))
        print(root.getchildren())










def Main():
    """main method"""
    wb = Workbook()
    wb.get_server_creds(f())
    wb.login()
    wb.get_workbooks()
    # print(wb.workbooks)
    wb.download_workbook(dl_path=None,
                         wb_name=None)
    wb.open_workbook_xml(f_path=None,
                         wb_name=None)
    wb.update_workbook_parameter("Parameter 1")


if __name__ == '__main__':
    Main()
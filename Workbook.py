import Tableau_Server
from Tableau_Server import *
import xml.etree.ElementTree as ET
import datetime
import time
from dateutil.parser import parse
import tempfile
import zlib
import zipfile
import shutil


class Node():
    """node class for xml tree traversing"""
    def __init__(self, value):
        """init"""
        self.head = value
        self.current = self.head
        self.next = None

    def get_next(self, value):
        """set the value of the next node"""
        self.next = value


class Workbook(TableauServer):
    """
        class:
            tableau workbook class
        superclass:
            TableauServer
    """

    def __init__(self):
        """init"""
        self.tableau_file = None
        self.tableau_zipfile = None
        self.tableau_workbook = None
        self.is_archived_file = False
        super().__init__()

    def download_workbook(self, dl_path, wb_name, new_wb_name):
        """download workbook of interest"""

        # set the path for the workbook to be downloaded
        try:
            if os.path.exists(dl_path):
                os.chdir(dl_path)
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
                    print('files saved ...\n')
                    for dl_path, _, new_wb_name in os.walk(dl_path):
                        for f in new_wb_name:
                            print(f)
                except ValueError:
                    print("workbook could not be downloaded\n")
        except ValueError as ve:
            print(ve)
        except Exception:
            print("uncaught workbook exception was raised\n")
        finally:
            print("exiting download process ...\n")

    def open_workbook_xml(self, f_path, wb_name):
        """check to see if tableau download is zipped"""
        try:
            if os.path.exists(f_path):
                try:
                    if os.path.isfile(f_path + '\\' + wb_name):
                        self.tableau_file = f_path + '\\' + wb_name
                        if zipfile.is_zipfile(self.tableau_file):
                            #--- zipfile parse code here
                            zip_file = zipfile.ZipFile(self.tableau_file)
                            self.tableau_workbook = self.tableau_file
                            archived_files = list(filter(lambda x: x.split('.')[-1] in ('twb', 'tds'),
                                                    zip_file.namelist()))
                            print("twbx archives: {}".format(archived_files))
                            self.tableau_workbook = zip_file.extract(*archived_files, path=f_path)
                            #print(type(self.tableau_workbook))
                        else:
                            #--- no zipfile process needed
                            self.tableau_workbook = self.tableau_file
                    else:
                        raise FileNotFoundError("Err[file could nto be located\n]")
                except FileNotFoundError as fe:
                    print(fe)
            else:
                raise OSError("path not found\n")
        except OSError as oe:
            print(oe)

    def update_workbook_parameter(self, parameter_name, tag_name, save=False):
        """update specific parameter in tableau workbook xml"""
        # create an instance of the Node class
        try:
            if isinstance(ET.parse(self.tableau_workbook), ET.ElementTree):
                self.tableau_workbook = ET.parse(self.tableau_workbook)
            else:
                raise TypeError("Err[workbook not converted to xml]\n")
        except TypeError as te:
            return te

        root = self.tableau_workbook.getroot()
        this_param = "'[{}]'".format(parameter_name)
        re_xml_search = ".//*[@name={}]/{}".format(this_param, tag_name)
        node_search = Node(value=root.find(re_xml_search))
        current = node_search.current

        child_current = current.getchildren()

        date_lambda = datetime.datetime.strptime((child_current[-1]
                                                  .attrib.get('value')
                                                  .strip('#')
                                                  .strip(' 00:00:00')),
                                                 "%Y-%m-%d")
        current_date = datetime.date.today()
        day_difference = int(str(datetime.date.today() - datetime.date(date_lambda.year,
                                                                       date_lambda.month,
                                                                       date_lambda.day)).split(" ")[0])
        print("day_difference: {}".format(day_difference))

        if day_difference >= 7:
            # the tableau xml needs to append a the most recent sunday date value
            date_tag = "#{}#".format(current_date)
            print('date tag: {}'.format(date_tag))
            attribute = current.makeelement('member', {'value': date_tag})
            print("adding attribute: {} ...".format(attribute))
            current.append(attribute)
            if save is True:
                wb_name = "tableau_workbook_{}.twb".format(current_date)
                self.tableau_workbook.write('C:\\Users\\wmurphy\\Desktop\\workbooks\\' + wb_name)
                print("saving workbook changes ...\n")
                os.remove('C:\\Users\\wmurphy\\Desktop\\workbooks\\DWM_1_30_18.twb')
            else:
                print('Changes not saved ... \n')

    def package_to_twbx(self):
        """create a twbx workbook that
        will be sent to tableau server"""
        os.chdir('C:\\Users\\wmurphy\\Desktop\\workbooks')
        twb_in = zipfile.ZipFile('18.twbx', 'r')
        twb_out = zipfile.ZipFile('WORKBOOK.twbx', 'w')
        for item in twb_in.infolist():
            buffer = twb_in.read(item.filename)
            if (item.filename[-4:] != '.twb'):
                twb_out.writestr(item, buffer)
        twb_out.write("Tableau_workbook_2018-02-27.twb")
        twb_out.close()
        twb_in.close()

    def publish(self, wb_path, wb_name, proj_id):
        """publish workbook to server"""
        wb_to_publish = TSC.WorkbookItem(name=wb_name, project_id=proj_id)
        wb_to_publish = self.creds_dict.get("server").workbooks.publish(wb_to_publish,
                                                                        wb_path, 'CreateNew')






















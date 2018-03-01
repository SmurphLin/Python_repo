import Tableau_Server
from Tableau_Server import *
import TempFiles
from TempFiles import *
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
        # --- from TempFiles class
        self.temp_file_exists = False
        self.wrkbk_is_published = False
        self.temp_file = TempFile()
       # --- Workbook parameters
        self.tableau_file = None
        self.tableau_zipfile = None
        self.tableau_workbook = None
        self.is_archived_file = False
        super().__init__()

    def get_workbook_from_srvr(self, workbook_name, new_name):
        """get workbook from the server"""
        self.temp_file.build_dir()    # if temp dir exists mk dir else, create and mk dir
        #print("temp file exists?  {}\n".format(tableau_temp_dir.temp_file_exists))
        if self.temp_file.temp_file_exists is True:
            self.temp_file_exists = True
        try:
            if workbook_name not in self.workbooks.keys():
                raise KeyError('Err[Workbook name is not associated with any keys]\n')
            else:
                wb_id = self.workbooks.get(workbook_name)   # workbook {name: id} found in dictionary
                try:
                    wb_file = self.creds_dict.get("server").workbooks.download(wb_id, str(os.getcwd()))
                except ValueError:
                    print('Workbook could not be downloaded! \n')
                except Exception:
                    print('uncaught exception was raised! \n')
        except KeyError as ke:
            print(str(ke))
        except Exception:
            print('uncaught exception was raised! \n')

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

    def read_xml_from_twb_twbx(self):
        """read the xml from twb or twbx file
        NOTE: dependeing on the file type, different
        methods exist for reading in the xml"""
        temp_files = [subfile for _, _, f in os.walk(str(os.getcwd())) for subfile in f]
        self.tableau_file = str(*temp_files)
        if zipfile.is_zipfile(self.tableau_file):
            # --- if file is .twbx then the xml is contained in a zipped file
            zip_file = zipfile.ZipFile(self.tableau_file)
            self.tableau_workbook = self.tableau_file
            archived_files = list(filter(lambda x: x.split('.')[-1] in ('twb', 'tds'),
                                         zip_file.namelist()))
            print("twbx archives: {}".format(archived_files))
            self.tableau_workbook = zip_file.extract(*archived_files, path=str(os.getcwd()))
        else:
            # --- if file is .twb then xml is easily accessible
            self.tableau_workbook = self.tableau_file

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


    def manage_xml_tags(self, param_name, t_name, is_child,save_changes=False):
        """manage the workbook's parameters through
        manipulation of workbook's xml"""
        if self.temp_file_exists is True:
            try:
                if isinstance(ET.parse(self.tableau_workbook), ET.ElementTree):
                    self.tableau_workbook = ET.parse(self.tableau_workbook)
                    root = self.tableau_workbook.getroot()
                    this_param = "'[{}]'".format(param_name)
                    if is_child is True:
                        re_xml_search = ".//*[@name={}]/{}".format(this_param, t_name)
                        node_search = Node(value=root.find(re_xml_search))
                    elif is_child is False:
                        re_xml_search = ".[@name={}]".format(this_param, t_name)
                        node_search = Node(value=root.find(re_xml_search))
                    else:
                        assert 1 == 0, 'Error! is_child not a boolean values \n'
                else:
                    raise TypeError("Err[workbook not converted to xml]\n")
            except TypeError as te:
                print(str(te))
        else:
            assert 1 == 0, "Workbook file does not exist!\n"



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
        self.wrkbk_is_published = True
        self.temp_file.workbook_is_published = self.wrkbk_is_published
        self.temp_file.tear_down_dir()
        self.logout()



def Main():
    wb = Workbook()

    #wb.get_server_creds(f_path=f())
    #wb.login()
    #wb.get_workbooks()
    #print(wb.workbooks)
    wb.get_workbook_from_srvr('New Queue Summary Today', new_name='new today')
    wb.read_xml_from_twb_twbx()

"""
    wb.download_workbook(dl_path='C:\\Users\\wmurphy\\Desktop\\workbooks',
                          wb_name='DWM_1/30/18', new_wb_name='18.twbx')
    wb.open_workbook_xml(f_path='C:\\Users\\wmurphy\\Desktop\\workbooks', wb_name='18.twbx')
    wb.update_workbook_parameter("Parameter 5", tag_name='members', save=True)
    wb.package_to_twbx()
    wb.publish(wb_path='C:\\Users\\wmurphy\\Desktop\\workbooks\\WORKBOOK.twbx',
               wb_name='ZIPPED_WORKBOOK',
               proj_id='d540a2b7-7547-4694-b508-7ef4cb4c2fbd')"""


if __name__=='__main__':
    Main()


























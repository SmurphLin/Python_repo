import os
import sys
import Tableau_Server
from Tableau_Server import *
import Workbook
from Workbook import *


class TempFile(object):
    """Temporary file storage for
    downloading tableau workbooks"""

    workbook_is_published = False
    temp_file_exists = False    # keep track of the temp file's existence
    parent_dir = None


    @classmethod
    def build_dir(cls):
        """creates a temporary directory
        as soon as a Tableau workbook is downloaded"""
        if os.path.exists('{}\\tableau'.format(os.getcwd())):
            cls.temp_file_exists = True
            temp = str(os.getcwd())
            cls.parent_dir = temp
            print('{}\\tableau exists, setting to current directory ...\n'.format(os.getcwd()))
            os.chdir('{}\\tableau'.format(os.getcwd()))
        else:
            print('creating {}\\tableau ... \n'.format(os.getcwd()))
            os.mkdir('{}\\tableau'.format(os.getcwd()))
            os.chdir('{}\\tableau'.format(os.getcwd()))
            cls.temp_file_exists = True

    @classmethod
    def tear_down_dir(cls, wrkbook):
        """remove the temorary directory
        as soon as the Tableau File has been
        successfully uploaded to the server"""
        if cls.workbook_is_published is True:
            # --- walk through the file system to find any files that need to be deleted
            temp_files = [subfile for _, _, f in os.walk(str(os.getcwd())) for subfile in f]
            os.remove(str(*temp_files))
            if len(temp_files) > 0:
                assert 1 == 0, 'Error: Temporary directory still contains files. Files must be deleted\n'
            else:
                tableau_dir = os.getcwd()
                os.chdir(cls.parent_dir)
                os.rmdir(tableau_dir)
                print('temporary directory has been deleted.\n')
                cls.temp_file_exists = False
        else:
            print("Cannot remove file, workbook has not been published \n")













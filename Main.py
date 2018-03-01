import Tableau_Server
from Tableau_Server import *
import Workbook
from Workbook import *
import Parameters
from Parameters import *


# --- initialize the Workbook class
workbook = Workbook()

# --- login to Tableau Server
workbook.get_server_creds(f_path=f())
workbook.login()

# --- get the names|ids of workbooks on the server
if workbook.workbooks is None:
    workbook.get_workbooks()




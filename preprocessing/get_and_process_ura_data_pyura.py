# use pyura package (https://github.com/eugenekoh/pyura) to download private residential property transaction records
# and then process the data (including conversion of SVY21 coordinates into lat/long using SVY21 class obtained from Github)

# THIS CODE DOESN'T SEEM TO WORK, maybe the package isn't working properly.

from pyura import Client
import os
import time
from dotenv import load_dotenv
load_dotenv()
URA_API_KEY = str(os.environ.get("URA_API_KEY"))

client = Client(URA_API_KEY)
client.get_token()
print("Sleep for 30 seconds before making api calls")
time.sleep(30)
batch_1 = client.private_resi_transaction(1)[0]
batch_2 = client.private_resi_transaction(2)[0]
batch_3 = client.private_resi_transaction(3)[0]
batch_4 = client.private_resi_transaction(4)[0]

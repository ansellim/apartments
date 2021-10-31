# 31 Oct 21
# Author: Ansel Lim
# Minimum code required to download one batch of URA private property transaction data
import requests

ura_api_key = "e7c58769-802c-454a-a0fc-4d06e98b0847"
ura_token = "74y94FcYacT77468FNvT4K06dg7X5a5S3-53BerzYes+8Xa0uzean869D24a9Y3PBRSwp2JxfswUN7Bgacs0y7-f-7ejevr9x6-7"
url = "https://www.ura.gov.sg/uraDataService/invokeUraDS"
params = {"service": "PMI_Resi_Transaction", "batch": "1"}
headers = {"Token": ura_token, "AccessKey": ura_api_key, "Accept-Encoding": "gzip,deflate,br",
           "Connection": "keep-alive", "User-Agent": "PostmanRuntime/7.26.8"}
response = requests.get(url, params=params, headers=headers)

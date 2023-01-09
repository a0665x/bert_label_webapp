from azure.storage.blob import BlobServiceClient , BlobClient
import json
from azure.core.pipeline.policies import HTTPPolicy
from azure.core.pipeline import Pipeline
from azure.core.pipeline.transport import RequestsTransport
from azure.storage.blob import ContainerClient
import jieba
import pandas as pd

# import logging
# import azure.functions as func

class NoLoggingPolicy(HTTPPolicy):
    def send(self, request, **kwargs):
        return self.next.send(request, **kwargs)
class BlobDataTransaction:
    def __init__(self,storage_account_key , storage_account_name , connection_string , container_name):
        self.storage_account_key = storage_account_key
        self.storage_account_name = storage_account_name
        self.connection_string = connection_string
        self.container_name = container_name

    def uploadToBlobStorage(self, local_path, file_name):
        blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
        blob_client = blob_service_client.get_blob_client(container=self.container_name, blob=file_name)
        with open(local_path, 'rb') as data:
            blob_client.upload_blob(data, overwrite=True)
        print(f'Uploaded data from {local_path} to {self.container_name}')
    def uploadJsonObjToBlobStorage(self, dict_data_obj,file_name):
        json_data = json.dumps(dict_data_obj)  # str_dict = json.dump(dict)
        json_io = json_data.encode()

        blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
        blob_client = blob_service_client.get_blob_client(container=self.container_name, blob=file_name)
        blob_client.upload_blob(json_io, overwrite=True)
        print(f'Uploaded Object_data to {self.container_name}')

    def uploadDfObjToBlob(self,dataframe, file_name):
        # Convert the dataframe to a CSV string
        csv_string = dataframe.to_csv(index=False)
        # Create a BlobDataTransaction object
        transaction = BlobDataTransaction(storage_account_key=self.storage_account_key,
                                          storage_account_name=self.storage_account_name,
                                          connection_string=self.connection_string,
                                          container_name=self.container_name)
        # Upload the CSV string to the blob
        blob_service_client = BlobServiceClient.from_connection_string(transaction.connection_string)
        blob_client = blob_service_client.get_blob_client(container=transaction.container_name, blob=file_name)
        blob_client.upload_blob(csv_string, overwrite=True)
        print(f'Uploaded data from dataframe to {transaction.container_name}')

    def downloadFileFromBlobStorage(self,file_name, local_path):
        # Create the BlobServiceClient object which will be used to create a container client
        blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)

        # Create a blob client using the container name and blob name
        blob_client = blob_service_client.get_blob_client(container=self.container_name, blob=file_name)

        # Download the blob to a file
        with open(local_path, "wb") as download_file:
            download_file.write(blob_client.download_blob().readall())
        print(f"Downloaded {file_name} to {local_path}")

    def downloadAsObjFromBlobStorage(self, file_name):
        # Create the BlobServiceClient object which will be used to create a blob client
        blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
        # Create a blob client using the container name and blob name
        blob_client = blob_service_client.get_blob_client(container=self.container_name, blob=file_name)
        # Download the blob as a stream
        blob_stream = blob_client.download_blob().readall()
        # Check the file extension and convert the stream to the appropriate object
        if file_name.endswith('.json'):
            # Convert the stream to a JSON object
            obj = json.loads(blob_stream)
        elif file_name.endswith('.csv'):
            # Convert the stream to a string
            obj = blob_stream.decode()
        elif file_name[-3:]=='txt':
            # Convert the stream to a string
            obj = blob_stream.decode()
        else:
            raise ValueError(f'Unsupported file extension: {file_name}')
        return obj


    def CheckBlobFlieExists(self,file_name_check):

        transport = RequestsTransport()
        pipeline = Pipeline(transport, policies=[NoLoggingPolicy()])

        blob_client = BlobClient.from_connection_string(
            conn_str=self.connection_string,
            container_name=self.container_name,
            blob_name=file_name_check,#blob_name = "hotel_article_1.txt"
            pipeline=pipeline)
        if blob_client.exists():
            print(f'{file_name_check} already exist in Azure Blob container ({self.container_name})')
            return True
        else:
            print(f'file not in Azure blob container ({self.container_name})')
            return  False
    def removeDataFromBlob(self, file_name):
        # Create the BlobServiceClient object which will be used to create a blob client
        blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
        # Create a blob client using the container name and blob name
        blob_client = blob_service_client.get_blob_client(container=self.container_name, blob=file_name)
        # Delete the blob
        try:
            blob_client.delete_blob()
            print(f'Successfully deleted {file_name} from {self.container_name}')
        except:
            print('file already has been removed')
            raise

    def checkBlobPaths(self):
        # Create a ContainerClient using the container name and connection string
        container_client = ContainerClient.from_connection_string(self.connection_string, self.container_name)

        # List all the blobs in the container
        blobs = container_client.list_blobs()

        # Extract the paths of all the blobs and return them as a list of strings
        return [blob.name for blob in blobs]

def JiebaCutWordCloud(sentence):
    seg_list = list(jieba.cut(sentence,cut_all=False))
    seg_list



# def main(req: func.HttpRequest) -> func.HttpResponse:
#     logging.info('Python HTTP trigger function processed a request.')
#
#     # Read the request body
#     body = req.get_body()
#     text = body.decode('utf-8')
#
#     # Convert the text to a dictionary object
#     text_dict = {"text": text}
#
#     # Create a BlobDataTransaction object
#     transaction = BlobDataTransaction(storage_account_key=storage_account_key,
#                                      storage_account_name=storage_account_name,
#                                      connection_string=connection_string,
#                                      container_name=container_name)
#     # Upload the dictionary object to the blob
#     transaction.uploadJsonObjToBlobStorage(text_dict, "NLP_dataset.csv")
#
#     return func.HttpResponse(f"Successfully added the text to the NLP_dataset.csv file: {text}")





if __name__ == "__main__":
    storage_account_key = "8O4CcWidAmAv+sFdraQ6VTsANHgiutP2mlbWBex41vPyxKgkLVfE4W71GUVsPOqcKWo76AmhkG1a+AStfEUeFA=="
    storage_account_name = "nlplabel"
    connection_string = f"DefaultEndpointsProtocol=https;AccountName={storage_account_name};AccountKey={storage_account_key};EndpointSuffix=core.windows.net"
    container_name = "labelfile"

    DT = BlobDataTransaction(storage_account_key , storage_account_name , connection_string , container_name)
    # ===file path upload===:
    # DT.uploadToBlobStorage('./prompt_txt/hotel_article_1.txt', 'hotel_article_1.txt')
    # ===checkpaths on blob===:
    paths = DT.checkBlobPaths()
    print('paths:',paths)
    # ===data Object upload===:
    data = dict({'Key':'Value'})
    DT.uploadJsonObjToBlobStorage(data , 'allen_label.json')
    # ===download blob path to localed===:
    # DT.downloadFileFromBlobStorage('hotel_article_to_blob.json', './prompt_txt/hotel_article_to_local.json')
    # DT.downloadFromBlobStorage('w_hotel.txt', './prompt_txt/w_hotel_blob.txt')
    # ===download File(txt/json) to local as a return Object===:
    obj = DT.downloadAsObjFromBlobStorage('allen_label.json')
    print(obj)
    # ===check filename exist on blob===:
    DT.CheckBlobFlieExists('allen_label.json')
    # # ===remove data from blob===:
    DT.removeDataFromBlob('allen_label.json')

    # JiebaCut('今天因為漏水,讓我很不高興')
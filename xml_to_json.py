
import os
from google.cloud import storage
import xmltodict, json
import xml.etree.ElementTree as ET
import pandas as pd
import datetime as dt

# The ID of your GCS bucket -GLOBAL
bucket_name = "apple_healthkit_ks"
local_file_path = "/Users/krithis/Documents/Fitness-Assistant/raw_data.xml"


def read_data(bucket_name):
    # The ID of your (XML) GCS object
    blob_name = "export.xml"
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    #blob_content = blob.download_as_text()
    blob.download_to_filename(local_file_path)
    #return blob_content

def write_data(bucket_name, file_name ,csv_string):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    csv_blob_name = file_name+'.csv'
    csv_blob = bucket.blob(csv_blob_name)
    #Upload extracted data to bucket
    csv_blob.upload_from_string(csv_string,content_type="text/csv")
    print(f'Wrote to gs://apple_healthkit_ks/{csv_blob_name}')
    return

def parse_xml_to_df(xml_file):

    # create element tree object
    tree = ET.parse(xml_file) 

    # for every health record, extract the attributes
    root = tree.getroot()
    record_list = [x.attrib for x in root.iter('Record')]

    #store it in df and explore (done in jhub)
    record_data = pd.DataFrame(record_list)

    # proper type to dates
    for col in ['creationDate', 'startDate', 'endDate']:
        record_data[col] = pd.to_datetime(record_data[col])

    # value is numeric, NaN if fails
    record_data['value'] = pd.to_numeric(record_data['value'], errors='coerce')

    # some records do not measure anything, just count occurences
    # filling with 1.0 (= one time) makes it easier to aggregate
    record_data['value'] = record_data['value'].fillna(1.0)

    # shorter observation names
    record_data['type'] = record_data['type'].str.replace('HKQuantityTypeIdentifier', '')
    record_data['type'] = record_data['type'].str.replace('HKCategoryTypeIdentifier', '')
    #record_data.tail()
    activity_data_csv=record_data.to_csv()
    write_data(bucket_name,"activity_data",activity_data_csv)
   

    workout_list = []

    for workout_element in root.iter('Workout'):
        workout_data = workout_element.attrib
        workout_statistics = workout_element.find('WorkoutStatistics')
        #workout_event = workout_element.find('WorkoutEvent')
        #workout_route = workout_element.find('WorkoutRoute')
    
        if workout_statistics is not None:
            workout_data['WorkoutStatistics'] = workout_statistics.attrib
        workout_list.append(workout_data)

    workout_data = pd.DataFrame(workout_list)
    workout_data_csv=workout_data.to_csv()
    write_data(bucket_name,"workout_data",workout_data_csv)
    return


#invoke function to download XML from bucket
read_data(bucket_name)

#invoke function to convert xml data into multiple csv files as needed
parse_xml_to_df(local_file_path)






''' EXTRA CODE SNIPPETS
    #not used
    def xml_to_json(xml_string):
        data = xmltodict.parse(xml_string)
        return json.dumps(data)

# xml_blob_content=read_data(bucket_name)

first_five_lines = xml_blob_content.split('\n')[:50]
for line in first_five_lines:
    print(line)

    # Mode can be specified as wb/rb for bytes mode.
    # See: https://docs.python.org/3/library/io.html
    # with blob.open("w") as f:
    #     f.write("Hello world")
    
    # Read the blob content
    #blob_content = blob.download_as_text()
    #csv_blob = bucket.blob(blob_name.replace('.xml', '.json'))

    # Split the content by lines, read and print the first two lines
    # first_two_lines = blob_content.split('\n')[:10]
    # for line in first_two_lines:
    #     print(line)


'''
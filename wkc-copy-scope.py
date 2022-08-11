# Method to copy a scope from a knowledeg accelerator structure to a organisation specific structure

from pandas import json_normalize

import json
import pandas as pd
import os
import requests
import sys
import time
import urllib3
import zipfile

# Lets set up some comon variables for the method
def setup_env():

    global cpd_host 
    global cs_host
    global username
    global password 
    global cs_username
    global cs_password 
    global headers
    global access_token
    global scope
    global session
    global working_dir
    
    cpd_host = "cpd-cpd-instance.apps.cp4d-4-0.os.fyre.ibm.com"
    cs_host = "cp-console.apps.cp4d-4-0.os.fyre.ibm.com"
    username = "admin"
    password = "Jtkrh2Z1762P"
    cs_username  = "admin"
    cs_password = "D3nWJ8Cm3psroFjIkxw4kvpUOssbGTzL"
    headers = {
        'Content-Type': "application/json",
        'Accept': "*/*",
        'Cache-Control': "no-cache",
        'Accept-Encoding': "gzip, deflate",
        'Content-Length': "56",
        'Connection': "keep-alive",
        'cache-control': "no-cache",
        'mime_type': "application/json"
        }
    session = requests.Session()
    working_dir = "/Users/neil/tmp"


# Generate a bearer token from provided CPD credentials. Note there is a difference when aim is enabled
def authorize( iamEnabled ):

    if( iamEnabled != "true" ):
      url = f"https://{cpd_host}/icp4d-api/v1/authorize"
      payload = {
        "username": username,
        "password": password
      }

      # When successfully authenticated token is stored in a global variable as below
      try:
          response = session.post(url,json=payload, verify=False)
      except:
          raise ValueError(f"Error authenticating... Check CPD_HOST, USERNAME, and PASSWORD argument values.")
    
      if response.status_code == 200:
          access_token = response.json()['token']
          headers['Authorization'] = f"Bearer {access_token}"
      else:
          raise ValueError(f"Error authenticating...\nResponse code: {response.status_code}\nResponse text:{response.text}")
    
    else:
      url = f"https://{cs_host}/idprovider/v1/auth/identitytoken"
      payload = {
        "Content-Type": "application/x-www-form-urlencoded",
        "grant_type": "password",
        "scope": "openid",
        "username": cs_username,
        "password": cs_password
      }

      # When successfully authenticated token is stored in a global variable as below
      try:
          response = session.post(url,json=payload, verify=False)
      except:
          raise ValueError(f"Error authenticating... Check CPD_HOST, USERNAME, and PASSWORD argument values.")
    
      if response.status_code == 200:

          iam_token = response.json()['access_token']
          url = f'https://{cpd_host}/v1/preauth/validateAuth' 

          tmp_headers = {
             "username": cs_username,
             "iam-token": iam_token
          }

          try:
            response = session.get(url, headers=tmp_headers,  verify=False)
            access_token = response.json()['accessToken']
            headers['Authorization'] = f"Bearer {access_token}"
          except:
            raise ValueError(f"Error authenticating... Check CPD_HOST, USERNAME, and PASSWORD argument values.")
      else:
          raise ValueError(f"Error authenticating...\nResponse code: {response.status_code}\nResponse text:{response.text}")



# Copy the scope we are insterested in 
def copy_scope( scope_name, enterprise_category_name ):

    # Get the cetgory id for the scope we are instered in
    scope_category_id = get_category_for_scope( scope_name )

    # Get or create if it doesn't exist the enterprise category
    enterprise_category_id = get_enterprise_category( enterprise_category_name  )

    # process the 
    processGovernanceArtifacts( scope_category_id )



def get_category_for_scope( scope_name ):

  url = url = f"https://{cpd_host}/v3/search"
  data = {
    "_source": ["metadata","entity", "categories", "category_id"],
    "query": {
      "bool": {
        "must": [
          { "query_string": { "query": scope_name, "fields":  ["metadata.name.keyword"] } },
          { "term": { "metadata.artifact_type": "category" }}
        ]
      }
    }
  }

  response = session.post(url, headers=headers, json=data, verify=False)

  if response.status_code != 200:
    raise ValueError(f"Error retrieving category: {response.text}")
  else:
    responseJson  = json.loads(response.text)
    if responseJson['size'] > 0:
      categories=json_normalize(responseJson['rows'])
      category_id=categories['entity.artifacts.artifact_id'][0]
      return category_id;



def get_enterprise_category( enterprise_category_name  ):

  enterprise_category_id = ""
  url = url = f"https://{cpd_host}/v3/search"
  data = {
    "_source": ["metadata","entity", "categories", "category_id"],
    "query": {
      "bool": {
        "must": [
          { "query_string": { "query": enterprise_category_name, "fields":  ["metadata.name.keyword"] } },
          { "term": { "metadata.artifact_type": "category" }}
        ]
      }
    }
  }

  response = session.post(url, headers=headers, json=data, verify=False)

  # Need to make tis more robust in case we have more categories with the same name
  if response.status_code == 200:
    responseJson  = json.loads(response.text)
    if responseJson['size'] > 0:
      enterprise_category=json_normalize(responseJson['rows'])
      enterprise_category_id=enterprise_category['entity.artifacts.artifact_id'][0]
  else:
    url = url = f"https://{cpd_host}/v3/categories"
    data = {
      "name": enterprise_category_name
    }

    response = session.post(url, headers=headers, json=data, verify=False)

    if response.status_code != 201:
      raise ValueError(f"Error retrieving category: {response.text}")
    else:
      responseJson  = json.loads(response.text)
      if responseJson['size'] > 0:
       resource=json_normalize(responseJson )
       enterprise_category_id=resource['artifact_id']

  return enterprise_category_id




def processGovernanceArtifacts( category_id ):

  url = url = f"https://{cpd_host}/v3/categories/{category_id}"
 
  data = {}

  response=session.get(url , headers=headers, json=data, verify=False )

  if response.status_code != 200:
    raise ValueError( response.text ) 
  else:
    responseJson=json.loads(response.text)
    artifacts=json_normalize(responseJson)
    asset_relationships = artifacts['entity.grouped_assets_rels'][0]

    #asset relationships is a list
    #{'metadata': {'artifact_type': 'relationship', 'artifact_id': '12a74496-583e-40e2-a676-82ed76d4aca9', 'version_id': '09b513a9-788f-4740-b458-208f4c4ae2cf_0', 
    #'source_repository_id': 'f7ddd0f1-095a-41d0-bc89-44b2feed21ba', 'source_repository_name': 'WKC_BG_f7ddd0f1-095a-41d0-bc89-44b2feed21ba', 
    #'global_id': 'f7ddd0f1-095a-41d0-bc89-44b2feed21ba_12a74496-583e-40e2-a676-82ed76d4aca9', 'created_by': '1000330999', 'created_at': '2022-06-23T20:10:03.254Z', 
    #'modified_by': '1000330999', 'modified_at': '2022-06-23T20:10:03.254Z', 'revision': '0', 'name': 'This is imported secondary category relationship', 
    #'state': 'PUBLISHED', 'read_only': False}, 'entity': {'relationship_type': 'grouped_by_category', 'source_type': 'category', 'target_type': 'glossary_term', 
    #'reference_copy': False, 'target_id': 'e6ea0a76-623d-498f-810e-4908b561f646', 'target_global_id': 'f7ddd0f1-095a-41d0-bc89-44b2feed21ba_e6ea0a76-623d-498f-810e-4908b561f646', 
    #'target_parent_category_id': '8a72919e-8c40-4a73-b190-4803deb2160d', 'target_name': 'Competitor Proximity', 'target_description': 'Identifies a Management Group which monitors competitor Organizations according to how near, geographically, they are to the Financial Institution.', 
    #'target_href': '/v3/categories/e6ea0a76-623d-498f-810e-4908b561f646', 'target_version_id': '83388022-3139-4e33-89f3-2e0144e6837c_0', 
    #'target_effective_start_date': '2022-06-23T20:08:28.931Z', 'source_id': '36ccad18-cf9e-4d8e-b226-d7e9d1334cfa', 'source_global_id': 'f7ddd0f1-095a-41d0-bc89-44b2feed21ba_36ccad18-cf9e-4d8e-b226-d7e9d1334cfa', 
    #'source_name': 'Customer Overview'}}

    # lets process the response and create the list of the primary categories and list of governance artifacts t
    primary_categories = []
    governance_artifacts = []
    for i in range( len(asset_relationships) ):
      primary_categories.append( asset_relationships[i]['entity']['target_parent_category_id'])
      governance_artifacts.append( [asset_relationships[i]['entity']['target_type'], asset_relationships[i]['entity']['target_id'], asset_relationships[i]['entity']['target_version_id']])
 
    #for debugging purposes
    ga_df = pd.DataFrame( governance_artifacts )
    ga_df.to_csv( working_dir + "/governance_artifacts.txt" )

    # lets remove the dupliactes from the list of primary categories
    primary_categories = list( set(primary_categories))  



    # Export all of the primnary categories
    export_categories( primary_categories )


    # Process each of the exports to remoive entries that are not in our list of artifacts
    process_exports( primary_categories, governance_artifacts )


    # Creat the category structure under our enterprise category



    # Load each of the primary category exports into our new structure


    # Cleanup
    cleanup( primary_categories )


# Export all of the governance artifacts that are in our business scope. This will write a zip file for each of the categories in scope
def export_categories( categories ):


  # export all the categories in one go this gives us a problem with duplicate reference data files
  # categoryids = ",".join(categories )
  # url =  f"https://{cpd_host}/v3/governance_artifact_types/export?category_ids={categoryids}"

  #so lets do it a category at a time
  data = {}
  for i in range( len(categories) ):
    url =  f"https://{cpd_host}/v3/governance_artifact_types/export?category_ids={categories[i]}"

    response=session.get(url , headers=headers, json=data, verify=False )

    if response.status_code != 200:
      raise ValueError( response.text ) 
    else:
      file = open(working_dir + "/category_" + categories[i] + ".zip", "wb")
      file.write(response.content)
      file.close()



# The exports contain all governance artifacts for each category that was exported. We need to process the exports so that only the governance artifacts taht are in our scope are 
# contained with the processed files
def process_exports( categories, governance_artifacts ):

   artifact_types = ['category', 'classification', 'data_class', 'glossary_term', 'policy', 'reference_data', 'rule' ]

   for i in range( len(categories) ):
     file_path = working_dir + "/category_" + categories[i]
     zip_file = working_dir +  "/category_" + categories[i] + ".zip"

     # lest unzip the files so we can work on the individual csv's
     with zipfile.ZipFile( zip_file ,"r") as zip_ref:
       zip_ref.extractall( file_path )
     
   
    # each zip file will contain directories for each glossary artifact type. Lets process them, deleting any empty files as we do so

     for j in range( len(artifact_types)):
       current_file_path = file_path + "/" + artifact_types[j]
       for curr_file in list_full_paths( current_file_path  ):
         if os.path.isfile(os.path.join( curr_file)):
            df = pd.read_csv( curr_file, keep_default_na=False) 
            if( df.empty ):
              os.remove( curr_file )
            else:
              print( "*** Processing file "  + curr_file )

              # Now we need to ensure that only governance artifacts in our scope are in the csv files
              # This code needs some work - the governance_artifacts is a list of lists.  the artifact ids that are in scope are in the second position of each row

              # This is too brutal - we are missing tags, classifications and any secondary categgories that are relevant

              governance_artifact_ids = []
              for sublist in governance_artifacts:
                governance_artifact_ids.append(sublist[1])
              #governance_artifact_ids.append( None ) 
              #governance_artifact_ids.append( '' ) 

              df = df.loc[df['Artifact ID'].isin(governance_artifact_ids)]
              # df = df.drop(columns=['Artifact ID'])
              df.to_csv( curr_file + ".new1.csv", index=False )
              
              # 
              #if artifact_types[j] == "glossary_term":
              #  process_term_file( curr_file, df, categories, governance_artifact_ids )



       # if the directory is empty remove it
       if len( os.listdir( current_file_path )) == 0:
         os.rmdir( current_file_path )
       elif len( os.listdir( current_file_path )) == 1 and artifact_types[j] == "reference_data":
        # Need some specific handling here for the reference data directory structure
         os.rmdir( current_file_path + "/reference_data_value" )
         os.rmdir( current_file_path )


def build_category_structure( top_level_category ):
    print( top_level_category)



def upload_terms_to_category( file_name, target_category ):

    url = f"https://{cpd_host}/v3/governance_artifact_types/import"

    files = {'file': (file_name, open(file_name, 'rb'), 'application/x-zip-compressed')}

    response = session.post( url, headers=headers, data=files, verify=False)

    if response.status_code != 202:
      raise ValueError(f"Error retrieving category: {response.text}")
    else:
      responseJson  = json.loads(response.text)



def process_term_file(curr_file, df, categories, governance_artifact_ids ):

    #governance_artifact_df = pandas.DataFrame()    
    # First make sure we only have artifact we're insterested in and their components
    # NOt sure there is a quick wa to do this without iterating over the entries in each file
    
    #categories.append('')

    #df = df.loc[ df['Secondary Categories'].isin(categories)]
    #df = df.drop(columns=['Artifact ID'])
    #df.to_csv( curr_file + ".new1.csv", index=False )


    #lets get the rows in the dataframe where our governance artifacts start
    governance_artifact_locations = df['Artifact ID'].isin(governance_artifact_ids)
    governance_artifact_locations = governance_artifact_locations.isin( True ) 
    print( governance_artifact_locations)

    #for i in range(len(df)):
    #  row = df.iloc[:i]

        
    #  if row['Artifact ID'].isin(governance_artifact_ids).any().any() :
    #    print( "Got some stuff we're interested in " + row['Name'])
    #    governance_artfact_df = row.copy()


    #    while processing_governance_artifact == True:
    #      row = df.iloc[:i+1]
        
    #      if row['Artifact ID'].isin(governance_artifact_ids).any().any() :
    #         print( "Got some stuff we're interested in " + row['Name'])
    #         governance_artfact_df.APPEND( row.copy() )
    #      else:
    #          processing_governance_artifact == True

    #  if row['Artifact ID'] == '' :
    #    print( "Got some stuff we're interested in " + row['Name'])
    #    governance_artfact_df = row.copy()


def process_reference_data_file( curr_file, df, categories, governance_artifact_ids  ):
  print("******* TO DO *********")

def cleanup( categories ):
   for i in range( len(categories) ):
     file_path = "category_" + categories[i] + ".zip"
     #os.remove(file_path) 


def finish():
    session.close()

def list_full_paths(directory):
    return [os.path.join(directory, file) for file in os.listdir(directory)]
 




# Needd some instructions how to invoke this
setup_env()
authorize( "true" )
copy_scope( "Customer Overview" , "Test")
#upload_terms_to_category( "/tmp/test.zip", "Redbooks" )
finish()


from requests import Session
import time
from base64 import b64encode
from json import dumps, load

# Function that logs usr in.
def login(username, password):
    
    # Encode the credentials in base64
    credentials = b64encode(f"{username}:{password}".encode()).decode('utf-8')

    # Create a session
    session = Session()

    # Make a GET request to the login endpoint with the Authorization header
    response = session.get('https://run.opencravat.org/server/login', headers={'Authorization': f'Basic {credentials}'})
 
    # Check the response
    if response.status_code ==  200 and response.content==b'"success"':
        print("Login successful!")
        return session
        # You can proceed with other requests using the session object
    else:
        print("Login failed. Status code:", response.status_code)
        print("Response:", response.text)
        
   
#Reads settings from JSON file and returns them for OpenCravat.
def oc_settings(json_file_path):
    # Read the JSON file
    with open(json_file_path, "r") as json_file:
        data = load(json_file)

    # Extract options from the JSON data
    options = data.get("options", {})
    
    # Convert the options dictionary to a JSON string
    options_json_str = dumps(options)
    
    # Manually construct the desired format
    formatted = {'options': options_json_str}
    
    return formatted


def cravat_report(vcf_filtered_file_path, annotated_file_name_path, username_oc, password_oc):
    
    #Initializes a session using usr login and password
    session = login(username_oc, password_oc)
    
    #Loads settings files for Open Cravat
    settings = oc_settings(json_file_path="scripts/settings/oc_settings.json")

    #Modify options depending on what you need.
    request = session.post('https://run.opencravat.org/submit/submit', 
                      files={'file_0':open(vcf_filtered_file_path)}, 
                      data=settings) 
    
    job_id= request.json()['id']
    
    print( job_id, "submitted!")
   
    #Continuosly checks whether job has finished. 
    job_status = session.get('https://run.opencravat.org/submit/jobs/' + job_id + '/status')
    time_elapsed = 0
   
    while job_status.json()['status'] != "Finished": 
        print(job_status.json()['status'])
        time.sleep(30)
        time_elapsed += 30
        print(time_elapsed/60, "Minutes elapsed since job submission")
        
        job_status = session.get('https://run.opencravat.org/submit/jobs/' + job_id + '/status')


    #Checks whether annotation has finished.        
    if job_status.json()['status'] == "Finished":         
        report = session.post('https://run.opencravat.org/submit/jobs/' + job_id + '/reports/vcf')

        while report.json() != "done":
             time.sleep(30)
             report = session.post('https://run.opencravat.org/submit/jobs/' + job_id + '/reports/vcf')

        if report.json() == "done":

            request_report = session.get('https://run.opencravat.org/submit/jobs/' + job_id + '/reports/vcf')
            
            with open(annotated_file_name_path, 'w') as file:
                file.write(request_report.text) 
                      
    
    return 0



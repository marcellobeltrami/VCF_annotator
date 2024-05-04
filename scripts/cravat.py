import requests
import time
import base64


# Function that logs usr in.
def login(username, password):
    
    # Encode the credentials in base64
    credentials = base64.b64encode(f"{username}:{password}".encode()).decode('utf-8')

    # Create a session
    session = requests.Session()

    # Make a GET request to the login endpoint with the Authorization header
    response = session.get('https://run.opencravat.org/server/login', headers={'Authorization': f'Basic {credentials}'})

    # Check the response
    if response.status_code == 200:
        print("Login successful!")
        return session
        # You can proceed with other requests using the session object
    else:
        print("Login failed. Status code:", response.status_code)
        print("Response:", response.text)
    



def cravat_report(vcf_filtered_file_path, annotated_file_name_path, username_oc, password_oc):
    
    #Initializes a session using usr login and password
    session = login(username_oc, password_oc)
    
    #Modify options depending on what you need.
    request = session.post('https://run.opencravat.org/submit/submit', 
                      files={'file_0':open(vcf_filtered_file_path)}, 
                      data={'options': '{"annotators": ["clinvar"], "reports": ["text"], "assembly": "hg38", "note": "test run"}'}) 
    
    # modify options here depending on information you want. Add annotars and notes and so on. 
    job_id= request.json()['id']
    
    print( job_id, "submitted!")
   
    #Continuosly checks whether job has finished. 
    job_status = session.get('https://run.opencravat.org/submit/jobs/' + job_id + '/status')
    time_elapsed = 0
   
    while job_status.json()['status'] != "Finished": 
        print(job_status.json()['status'])
        time.sleep(5)
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


#login()
#cravat_report("/home/marcello/Thesis_dev/VCF_annotator/scripts/test.vcf", "./annotated.vcf")


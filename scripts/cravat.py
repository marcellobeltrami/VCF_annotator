import requests
import time


def cravat_report(file_name_str, vcf_filtered_file_path, annotated_file_name_path):
   
    request = requests.post('https://run.opencravat.org/submit/submit', 
                      files={file_name_str:open(vcf_filtered_file_path)}, 
                      data={'options': '{"annotators": ["clinvar"], "reports": ["text"], "assembly": "hg38", "note": "test run"}'}) 
    # modify options here depending on information you want. Add annotars and notes and so on. 
    
    job_id= request.json()['id']
    
    print(job_id, "submitted!")

    #Continuosly checks whether job has finished. 
    job_status = requests.get('https://run.opencravat.org/submit/jobs/' + job_id + '/reports')
    time_elapsed = 0 
    while job_status.json()['status'] != "Finished": 
        time.sleep(30)
        time_elapsed += 30
        print(time_elapsed/60, "Minutes elapsed since job submission")
        
        job_status = requests.get('https://run.opencravat.org/submit/jobs/' + job_id + '/reports')
        


    #Checks whether annotation has finished.        
    if job_status.json()['status'] != "Finished":         
        report = requests.post('https://run.opencravat.org/submit/jobs/' + job_id + '/reports/vcf')

        while report.json() != "done":
             time.sleep(30)
             report = requests.post('https://run.opencravat.org/submit/jobs/' + job_id + '/reports/vcf')

        if report.json() == "done":

            request_report = requests.get('https://run.opencravat.org/submit/jobs/' + job_id + '/reports/vcf')
            
            with open(annotated_file_name_path, 'w') as file:
                file.write(request_report.text) 
                      
    
    return 0

    


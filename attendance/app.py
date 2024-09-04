from flask import Flask, request, render_template, redirect, url_for
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# Function to fetch hidden fields
def fetch_hidden_fields(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    viewstate = soup.find('input', {'name': '__VIEWSTATE'})['value']
    viewstate_generator = soup.find('input', {'name': '__VIEWSTATEGENERATOR'})['value']
    event_validation = soup.find('input', {'name': '__EVENTVALIDATION'})['value']
    
    return viewstate, viewstate_generator, event_validation

# Function to get attendance details
def get_attendance_details(url, reg_no, viewstate, viewstate_generator, event_validation):
    payload = {
        '__VIEWSTATE': viewstate,
        '__VIEWSTATEGENERATOR': viewstate_generator,
        '__EVENTVALIDATION': event_validation,
        'TxtRegno': reg_no,
        'Button1': 'Submit'
    }
    
    response = requests.post(url, data=payload)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    result = {}
    result['AdminNo'] = soup.find('span', {'id': 'Label1'}).text.strip()
    result['Name'] = soup.find('span', {'id': 'Label2'}).text.strip()
    
    table = soup.find('table', {'id': 'GridView1'})
    if table:
        rows = table.find_all('tr')[1:]
        result['Records'] = []
        for row in rows:
            columns = row.find_all('td')
            record = {
                'CCode': columns[0].text.strip(),
                'Semno': columns[1].text.strip(),
                'RegNo': columns[2].text.strip(),
                'AdmnNo': columns[3].text.strip(),
                'SName': columns[4].text.strip(),
                'Total': columns[5].text.strip(),
                'Present': columns[6].text.strip(),
                'Absent': columns[7].text.strip(),
                'OD': columns[8].text.strip(),
                'Percentage': columns[9].text.strip()
            }
            result['Records'].append(record)
    
    return result

# Define route for the homepage
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        reg_no = request.form.get('reg_no')
        if reg_no:
            try:
                viewstate, viewstate_generator, event_validation = fetch_hidden_fields(url)
                attendance_details = get_attendance_details(url, reg_no, viewstate, viewstate_generator, event_validation)
                return render_template('result.html', attendance_details=attendance_details)
            except Exception as e:
                return render_template('result.html', error=str(e))
    
    return render_template('index.html')

# URL of the attendance page
url = 'https://www.sadakath.ac.in/attendance2.aspx'

if __name__ == '__main__':
    app.run(debug=True)

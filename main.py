from flask import Flask, request, render_template, jsonify
from datetime import datetime, timedelta
import json
import dut

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        data = request.get_json(force=True)
        username = data['username']
        password = data['password']
        return dut.login(username, password)
    else:
        return render_template('login.html')

@app.route('/getCal', methods=["POST"])
def queryCal():
    data = request.get_json(force=True)
    datecode = data['datecode']
    cookie = data['cookie']
    return dut.getCal(datecode, cookie)

@app.route('/getWeekInTerm', methods=["GET"])
def getWeek():
    
    # get args
    term = str(request.args.get("term"))

    # load term data
    with open("term.json", "r") as file:
        term_data = json.loads(file.read())
        file.close()

    week_start_number = term_data[term]["weekstart"]
    start_date = term_data[term]["start"]
    end_date = term_data[term]["end"]


    # Convert string dates to datetime objects
    start_date = datetime.strptime(start_date, "%d/%m/%Y")
    end_date = datetime.strptime(end_date, "%d/%m/%Y")
    
    current_start = start_date
    current_week_number = week_start_number
    
    # Mapping of English weekdays to Vietnamese
    vietnamese_weekdays = {
        "Monday": "Thứ 2",
        "Tuesday": "Thứ 3",
        "Wednesday": "Thứ 4",
        "Thursday": "Thứ 5",
        "Friday": "Thứ 6",
        "Saturday": "Thứ 7",
        "Sunday": "Chủ Nhật"
    }
    
    weeks = {}
    while current_start <= end_date:
        week_days = {}
        for i in range(7):
            current_day = current_start + timedelta(days=i)
            if current_day > end_date:
                break  # Stop if the current day exceeds the term's end date
            # Get the Vietnamese weekday name
            vietnamese_weekday = vietnamese_weekdays[current_day.strftime('%A')]
            week_days[vietnamese_weekday] = current_day.strftime("%d/%m/%Y")
        
        weeks[current_week_number] = week_days
        
        current_start += timedelta(days=7)  # Move to the next Monday
        current_week_number += 1  # Increment the week number
    
    return jsonify(weeks)

@app.route("/getTimetable")
def getTimetable():
    with open("timetable.json", "r") as file:
        data = json.loads(file.read())
        file.close()
    return jsonify(data)


app.run('0.0.0.0')
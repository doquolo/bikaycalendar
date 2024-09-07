from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from datetime import datetime, timedelta
import convertTableToJson
from ics import Calendar, Event
import pytz
import json
import time
import io
import PySimpleGUI as sg
sg.theme("SystemDefaultForReal")

# function for generating date range
def generate_date_range(start_date, end_date):
    # Parse the input strings into datetime objects
    start = datetime.strptime(start_date, "%d/%m/%Y")
    end = datetime.strptime(end_date, "%d/%m/%Y")

    # Generate the date range
    date_range = []
    current_date = start
    while current_date <= end:
        # Format each date as dd/mm/yyyy and append to the list
        date_range.append(current_date.strftime("%d/%m/%Y"))
        current_date += timedelta(days=1)

    return date_range

# launch chrome driver headless
chrome_options = Options()
chrome_options.add_argument("--headless=new")
driver = webdriver.Chrome(chrome_options)

# login function
def login(id, passwd):
    # navigate to url
    url = 'http://sv.dut.udn.vn'
    driver.get(url)

    # search for login button
    driver.find_element(By.ID, 'linkDangNhap').click()

    # fill in credentials
    ## get login url
    loginPageURL = driver.current_url
    ## id
    driver.find_element(By.ID, 'DN_txtAcc').send_keys(id)
    ## password
    driver.find_element(By.ID, 'DN_txtPass').send_keys(passwd)
    ## hit login
    driver.find_element(By.ID, 'QLTH_btnLogin').click()
    # wait for a bit
    time.sleep(.50)
    if (loginPageURL != driver.current_url):
        return driver.find_element(By.ID, 'Main_lblHoTen').get_attribute("textContent")
    else:
        return False

    
def exportCal(path, start_date, end_date):
    
    # navigate to schedule panel
    ActionChains(driver).move_to_element(driver.find_element(By.ID, "lPaCANHAN")).perform()
    driver.find_element(By.ID, 'lCoCANHAN03').click()

    # generate daterange
    datelist = generate_date_range(start_date.strip(), end_date.strip())

    # load up timetable
    with open("timetable.json", encoding="utf-8") as timetable_raw:
        timetable = json.loads(timetable_raw.read())
        timetable_raw.close()

    # create a calendar
    calendar = Calendar()
    # timezone
    local = pytz.timezone("Asia/Ho_Chi_Minh")

    layout = [
        [sg.Text("Tiến trình quét: ", key="-progress_status-")],
        [sg.ProgressBar(max_value=len(datelist), key="-progress_bar-", orientation='horizontal', size=(50, 1))]
    ]

    window = sg.Window("Đang quét lịch ~", layout, finalize=True)
    while True:
        # scraping by date
        for date in datelist:
            # update gui
            window['-progress_bar-'].update(current_count=datelist.index(date) + 1)
            window['-progress_status-'].update(f"Tiến trình quét: {date}")

            # input date
            datefield = driver.find_element(By.ID, "LHTN_txtNgay")
            datefield.clear()
            datefield.send_keys(date)
            driver.find_element(By.ID, "MainContent_LHTN_btnDuLieu").click()

            # wait for data to be fetched
            status = driver.find_element(By.ID, "LHTN_status")
            while (len(status.find_elements(By.XPATH, "./*")) > 0):
                time.sleep(.25)

            # get data
            data = driver.find_element(By.ID, "LHTN_Grid").get_attribute("innerHTML")
            # convert to json
            dataJson = convertTableToJson.tableToJS(data)

            # log out data
            if (len(dataJson) != 0):
                for subject in dataJson:
                    # parsing data
                    tkb = subject['Thời khóa biểu'].split(",")
                    period = tkb[1]
                    period_split = period.split("-")
                    duration = [timetable[period_split[0]]["start"], timetable[period_split[1]]["end"]]

                    # create a new event
                    event = Event()
                    event.name = f"Môn: {subject['Tên lớp học phần']}"
                    event.description = f"Giảng viên: {subject['Giảng viên']} - Tiết: {period} - Mã môn học: {subject['Mã']}"
                    event.location = tkb[2]
                    event.begin = (local.localize(datetime.strptime(f"{subject['Ngày học']}-{duration[0]}", "%d/%m/%Y-%H:%M")).astimezone(pytz.utc)).strftime("%Y-%m-%d %H:%M:%S")
                    event.end = (local.localize(datetime.strptime(f"{subject['Ngày học']}-{duration[1]}", "%d/%m/%Y-%H:%M")).astimezone(pytz.utc)).strftime("%Y-%m-%d %H:%M:%S")

                    # add to calendar
                    calendar.events.add(event)
        break
    window.close()


    with open(path, 'w', encoding='utf-8') as my_file:
        serialized_calendar = calendar.serialize().replace('\n', '')
        my_file.writelines(serialized_calendar)
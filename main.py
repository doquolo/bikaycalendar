import PySimpleGUI as sg
sg.theme("SystemDefaultForReal")
from datetime import datetime
import backend

login = [
    [sg.Text("Nhập mã SV:    "), sg.In(key="-mssv-", size=(34,1))],
    [sg.Text("Nhập mật khẩu: "), sg.In(key="-pass-", password_char="*", size=(34,1))],
    [sg.Button("Đăng nhập", key="-login-")],
    [sg.Text(key='-welcometext-', visible=False)],
]

today = datetime.now()
calPanel = [
    [sg.Input(key='-start-', size=(20,1)), sg.CalendarButton('Ngày bắt đầu',  target='-start-', format='%d/%m/%Y', default_date_m_d_y=(today.month, today.date, today.year), month_names=('Tháng 1', 'Tháng 2', 'Tháng 3', 'Tháng 4', 'Tháng 5', 'Tháng 6', 'Tháng 7', 'Tháng 8', 'Tháng 9', 'Tháng 10', 'Tháng 11', 'Tháng 12'), day_abbreviations=('T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'CN'))],
    [sg.Input(key='-end-', size=(20,1)), sg.CalendarButton('Ngày kết thúc',  target='-end-', format='%d/%m/%Y', default_date_m_d_y=(today.month, today.date, today.year), month_names=('Tháng 1', 'Tháng 2', 'Tháng 3', 'Tháng 4', 'Tháng 5', 'Tháng 6', 'Tháng 7', 'Tháng 8', 'Tháng 9', 'Tháng 10', 'Tháng 11', 'Tháng 12'), day_abbreviations=('T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'CN'))],
    [sg.Text('Đường dẫn lưu lịch: '), sg.In(size=(25,1), enable_events=True ,key='-path-'), sg.FolderBrowse("Mở")],
    [sg.Button("Xuất lịch học", disabled=True, key="-export-"), sg.Text(" đuôi (.ics)")]
]

layout = [
    [sg.Frame('Đăng nhập', login)],
    [sg.Frame('Xuất lịch học', calPanel)],
    [sg.StatusBar("Sẵn sàng", key='-status-', relief=sg.RELIEF_FLAT, pad=(0, 0), expand_x=True)]
]

win = sg.Window("BKcalendar", layout, finalize=True)

while True:
    e, v = win.read()
    if (e == sg.WIN_CLOSED):
        break
    if (e == '-path-'):
        folder = v['-path-'] 
    if (e == "-login-"):
        welcome_text = backend.login(v['-mssv-'], v['-pass-'])
        if (welcome_text == False):
            sg.popup("Đăng nhập thất bại, vui lòng kiểm tra lại mssv hoặc mật khẩu :(", title="Thông báo")
        else:
            sg.popup("Đăng nhập thành công!", title="Thông báo")
            win['-status-'].update("Đã đăng nhập")
            win['-welcometext-'].update(visible=True)
            win['-welcometext-'].update(welcome_text)
            win['-login-'].update(disabled=True)
            win['-export-'].update(disabled=False)
    if (e == "-export-"):
        path = v['-path-'] + "/lich.ics"
        backend.exportCal(path, v['-start-'], v['-end-'])
        ans = sg.popup(f"Hoàn tất! Lịch của bạn đã được lưu tại đường dẫn\n{path}", title="Thông báo", line_width=100)


backend.driver.quit()
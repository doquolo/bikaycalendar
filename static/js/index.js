// variables
let cookie = null;
let subjectList = [];
let weekInTerm;
let timetable;

const createCheckboxList = (list) => {
    let container = document.querySelector("#subjectPickerContainer");
    container.innerHTML = `<tr style="font-weight: 600;">
          <td>Nhập?</td>
          <td>Tên môn</td>
          <td>Giảng viên</td>
        </tr>`;
    for (let i in list) {
        var elem = `
        <tr>
            <td>
                <input type="checkbox" id="subjectPicker" value="${i}" checked />
            </td>
            <td>${list[i].name}</td>
            <td>${list[i].profName}</td>
        </tr>
      `;
        container.innerHTML += elem;
    };
    container.innerHTML += `<td colspan="3" class="button" style="text-align: center; height: auto !important; width: auto Im !important;" onclick="addSubject()"> ➕ Thêm môn học</td>`;
};

const convertToSubjectObject = (data) => {
    console.log(data);
    const tkb_raw = String(data['Thời khóa biểu']).trim().split(";");
    const studyweek = String(data['Tuần học']).trim().split(";");

    let subjectDetail = {
        name: data['Tên lớp học phần'],
        profName: data['Giảng viên'],
        periodLists: []
    };

    for (let weekPart in studyweek) {

        // week data 
        const week = studyweek[weekPart].trim().split('-');
        const weekStart = Number(week[0]);
        const weekEnd = Number(week[1]);

        // tkb data
        for (let tkbIndex in tkb_raw) {
            const tkb = (tkb_raw[tkbIndex]).trim().split(",");
            const weekday = tkb[0];
            const period = (tkb[1]).trim().split("-");
            const location = tkb[2];
            for (let j = weekStart; j < weekEnd + 1; j++) {
                const timeStart = moment(`${weekInTerm[j][weekday]} ${timetable[period[0]]['start']}`, "DD/MM/YYYY HH:mm").toDate();
                const timeEnd = moment(`${weekInTerm[j][weekday]} ${timetable[period[1]]['end']}`, "DD/MM/YYYY HH:mm").toDate();
                subjectDetail.periodLists.push({
                    location: location,
                    timeStart: timeStart,
                    timeEnd: timeEnd
                });
            }
        }
    }

    subjectList.push(subjectDetail);
}

const addSubject = () => {
    const name = prompt("Nhập tên lớp học phần:");
    const profName = prompt("Nhập tên giảng viên:")
    const studyweek = prompt("Nhập tuần học:\nVD: 7-14;19-22 | Tuần 7-14; Tuần 19-22");
    const tkb_raw = prompt("Nhập TKB:\nVD: Thứ 4,1-3,H307; Thứ 7,3-5,H303 | Thứ 4 (Tiết 1-3) H307 - Thứ 7 (Tiết 3-5) H303");
    convertToSubjectObject({"Tuần học": String(studyweek), "Tên lớp học phần": String(name), "Thời khóa biểu": String(tkb_raw), "Giảng viên": String(profName)});
    createCheckboxList(subjectList);
}

const handleSubjectPicker = () => {
    const createCal = (data) => {
        var cal = ics();
        data.forEach(subject => {
            const subjectName = `Môn: ${subject.name}`;
            const description = `GV: ${subject.profName}`;
            subject.periodLists.forEach(period => {
                cal.addEvent(subjectName, description, period.location, period.timeStart, period.timeEnd);
            })
        });
        let filename = `${document.querySelector("#username").value} - ${document.querySelector("#hockipicker").selectedOptions[0].label} ${document.querySelector("#nampicker").value}`
        cal.download(filename);
    };
    let pickerList = document.querySelectorAll("#subjectPicker");
    let selectedSubjectList = [];
    pickerList.forEach(element => {
        if (element.checked) {
            selectedSubjectList.push(subjectList[element.value]);
        }
    });
    createCal(selectedSubjectList);
};

document.addEventListener("DOMContentLoaded", () => {
    document.querySelector("#loginbtn").addEventListener("click", () => {
        document.querySelector("#loginbtn").disabled = true;
        document.querySelector("#loginbtn").value = "Đang đăng nhập...";
        const username = document.querySelector("#username").value;
        const password = document.querySelector("#password").value;
        if (username == "" || password == "") alert("MSSV hoặc mật khẩu không được để trống!");
        else {
            document.querySelector("#loginbtn").disabled = true;
            fetch("/login", {
                method: "POST",
                body: JSON.stringify({ 'username': username, 'password': password })
            })
                .then(req => {
                    return req.json()
                })
                .then(req => {
                    if (req.status == "success") {
                        cookie = req.cookie;
                        document.querySelector("#welcome_text").textContent = req.name;
                        document.querySelector("#loginpanel").style.display = 'none';
                        document.querySelector("#mainpanel").style.display = 'flex';
                    } else {
                        alert("Kiểm tra lại mssv và mật khẩu :(");
                        document.querySelector("#loginbtn").disabled = false;
                        document.querySelector("#loginbtn").value = "Đăng nhập";
                    }
                })
        }
    })
    document.querySelector("#nampicker").value = new Date().getFullYear();
    document.querySelector("#getData").addEventListener('click', () => {
        document.querySelector("#getData").disabled = true;
        document.querySelector("#getData").value = "Đang lấy dữ liệu...";
        const datecode = `${(document.querySelector('#nampicker').value) % 100}${document.querySelector('#hockipicker').value}`
        fetch(`/getCal`, {
            method: 'POST',
            body: JSON.stringify({
                datecode: datecode,
                cookie: cookie
            })
        })
            .then(req => { return req.text() })
            .then(res => {
                document.querySelector("#data").innerHTML = res;

                document.querySelector("#TTKB_GridInfo > tbody > tr:nth-child(1)").remove();
                const child = document.createElement('th');
                child.innerHTML = '<th class="GridHeaderCell" width="30">TT</th>';
                document.querySelector("#TTKB_GridInfo > tbody > tr:nth-child(1)").prepend(child);

                // document.querySelector("#mainpanel").style.bottom = 'unset';

                const schedule = tableToJSON("TTKB_GridInfo");
                schedule.pop();
                console.log(schedule);
                parseToCal(schedule);
            })
    })

    function tableToJSON(tableId) {
        // Get the table element
        const table = document.getElementById(tableId);
        const headers = [];
        const data = [];

        // Get headers from the first row of the table (assuming headers are in the first row)
        const headerCells = table.querySelectorAll('tr.GridHeader th');
        headerCells.forEach(header => headers.push(header.innerText.trim()));

        // Get rows from tbody
        const rows = table.querySelectorAll('tbody tr.GridRow');
        rows.forEach(row => {
            const cells = row.querySelectorAll('td');
            const rowData = {};
            cells.forEach((cell, index) => {
                // Avoid adding data if index exceeds header length
                if (index < headers.length) {
                    rowData[headers[index]] = cell.innerText.trim();
                }
            });
            data.push(rowData);
        });

        return data
    }

    async function parseToCal(schedule) {
        await fetch(`/getWeekInTerm?term=${document.querySelector('#hockipicker').value}`)
            .then(req => { return req.json() })
            .then(res => weekInTerm = res);
        await fetch(`/getTimetable`)
            .then(req => { return req.json() })
            .then(res => timetable = res);
        subjectList = [];
        for (let i in schedule) {
            convertToSubjectObject(schedule[i]);
        }
        document.querySelector("#getData").disabled = false;
        document.querySelector("#getData").value = "Lấy dữ liệu";
        createCheckboxList(subjectList);
        document.querySelector("#subjectForm").style.visibility = 'visible';

    }
})
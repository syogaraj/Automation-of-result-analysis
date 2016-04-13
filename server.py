import os

from flask import Flask, render_template, request
from selenium import webdriver
from selenium.webdriver.support.ui import Select
# addl. modules
import lxml.html as html
from lxml.html.clean import Cleaner
from werkzeug.contrib.cache import FileSystemCache  # pip install werkzeug
import plotly.plotly as py
import plotly.graph_objs as go
from openpyxl import Workbook

app = Flask(__name__)


@app.route('/')
def initial():
    return render_template("index.html")


@app.route('/confirm', methods=['POST'])
def write():
    subjects = []
    first_part = request.form["first_part"]
    start_num = request.form["start_num"]
    end_num = request.form["end_num"]
    semester = request.form["sem"]
    dept = request.form["dept"]
    subjects.append(''.join((request.form["subject_1"]).split()))
    subjects.append(''.join((request.form["subject_2"]).split()))
    subjects.append(''.join((request.form["subject_3"]).split()))
    subjects.append(''.join((request.form["subject_4"]).split()))
    subjects.append(''.join((request.form["subject_5"]).split()))
    if len(request.form["subject_6"]) != 0:
        subjects.append(''.join((request.form["subject_6"]).split()))
    subjects.append(''.join((request.form["pr_1"]).split()))
    subjects.append(''.join((request.form["pr_2"]).split()))
    subjects.append(''.join((request.form["pr_3"]).split()))
    return number_gen(first_part, int(start_num), int(end_num), semester, dept, subjects)


def number_gen(first_part, start_num, end_num, semester, dept, subjects):
    driver = webdriver.Firefox()  # Firefox used for testing. Change it to PhantomJS
    driver.implicitly_wait(30)
    base_url = "http://result.pondiuni.edu.in/candidate.asp"
    url = base_url
    driver.get(base_url)
    # os.mkdir(str(first_part))
    os.chdir("results")
    os.chdir(str(first_part))
    cache = FileSystemCache('.cachedir', threshold=100000)
    for number in range(start_num, end_num + 1):
        current_num = "%04d" % number
        numb = first_part + str(current_num)
        driver.find_element_by_id("txtregno").clear()
        driver.find_element_by_id("txtregno").send_keys(numb)
        Select(driver.find_element_by_id("cmbdegree")).select_by_visible_text(dept)
        Select(driver.find_element_by_id("cmbexamno")).select_by_visible_text(semester)
        driver.find_element_by_id("button1").click()

        # copying the content
        page_source = cache.get(url)
        page_source = driver.page_source
        cache.set(url, page_source, timeout=60 * 60 * 24 * 7)  # week in seconds
        root = html.document_fromstring(page_source)
        Cleaner(kill_tags=['noscript'], style=True)(root)  # lxml >= 2.3.1

        # pasting to file
        filename = str(numb) + ".txt"
        fp = open(filename, 'w')
        fp.write((root.text_content()).encode('utf-8'))
        fp.close()
        driver.back()
    driver.close()
    return analyze(subjects)


def is_fail(data):
    try:
        data.index('F')
    except ValueError:
        return False
    else:
        return True


def is_fully_absent(data):
    try:
        if data.count('FA') == 6:
            return True
    except:
        return False

def analyze(subjects):
	
	subject = ["CommunicationEngineering-II", "SoftwareEngineering", "OperatingSystems", "DataBaseManagementSystems",
		       "TheoryofComputation", "CommunicationEngineeringLab", "OperatingSystemsLab", "DataBaseManagementSystemsLab",
		       "ComputerHardware&Troubleshooting", "GeneralProficiency-I"]

	college = ["smvec", "mit", "pkiet", "alpha", "bharathiyar", "christ", "pec", "krishna", "rajiv", "sjs", "ganesh",
		       "mec"]

	for coll in college:
		exec ("%s=%s" % (coll, {}))

	for c in college:
		exec ("temp = " + c)
		temp.update({'total': 0})

	smvec.update({"total": 0})

	colleges = {"1034\xc2\xa0": "smvec",
		        "1039\xc2\xa0": "mit",
		        "1035\xc2\xa0": "rajiv",
		        "1031\xc2\xa0": "pec",
		        "1033\xc2\xa0": "bharathiyar",
		        "1037\xc2\xa0": "christ",
		        "1038\xc2\xa0": "pkiet",
		        "1090\xc2\xa0": "krishna",
		        "1042\xc2\xa0": "sjs"
		        }

	os.chdir("/run/media/yogaraj/Virus-Restricted/Mini Project try/Web_UI/results/13TH")
	for fi in os.listdir(os.getcwd()):
		if fi.endswith(".txt"):
		    print fi
		    with open(fi, "r") as files:
		        data = files.readlines()
		        data = ["".join(i.split()) for i in data]
		        data = data[::-1]
		        if "InvalidRegister/RollNo.!" in data:
		            continue

		        for lines in data:
		            if lines.startswith("College"):
		                inst = colleges.get(lines[8:])
		                # if inst != "smvec": continue
		                exec ("col=%s" % inst)
		                if not is_fully_absent(data):
		                    col.update({"total": col.get("total") + 1})
		                else:
		                    break


		            elif len(lines) <= 2 and lines.isalpha() and lines in "SABCDE":
		                # print lines
		                flag = True

		            elif len(lines) <= 2 and lines.isalpha() and lines in "FAF":
		                flag = False

		            elif lines in subject:
		                sub = subject[subject.index(lines)]
		                # print sub
		                if flag:
		                    try:
		                        col.update({sub: col.get(sub) + 1})
		                    except:
		                        col.update({sub: 1})
		                flag = False

	data = []
	for c in college:
		exec ("col=" + c)
		for_grah = {}
		total_stud = col.get("total")
		for key, value in col.items():
		    if key == "total": continue
		    perc = (value / float(total_stud)) * 100.0
		    if perc > 100:
		        perc = 100
		    print key, "%.2f" % perc
		    for_grah.update({key: "%.2f" % perc})
		if c=="smvec":
		    csmvec = [go.Bar(
		        x = for_grah.keys(),
		        y = for_grah.values()
		    )]
		elif c=="mit":
		    cmit = [go.Bar(
		        x = for_grah.keys(),
		        y = for_grah.values()
		    )]
		names = c + str(1)
		exec(names +"=go.Bar(x="+str(for_grah.keys())+",y="+str(for_grah.values())+")")
		# names['name'] = c
		exec('temp='+names)
		temp['name'] = c
		data.append(temp)

	layout = go.Layout(barmode="group")
	fig = go.Figure(data=data, layout=layout)
	plot_url = py.plot(fig, filename='Result analysed')

if __name__ == "__main__":
    app.run(debug=True)

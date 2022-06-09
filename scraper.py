import requests
from bs4 import BeautifulSoup
import requests
import unicodedata
import os
import pdfkit
import json
from weasyprint import HTML
from bs4 import BeautifulSoup, SoupStrainer
from tika import parser
from urllib.parse import urlparse, urljoin

#outputs a list of strings containing course numbers for a given department
def CourseList(dept, level):
	url = 'http://catalog.gatech.edu/courses-{1}/{0}'.format(dept, level)
	if level == "all":
		url = 'http://catalog.gatech.edu/coursesaz/{0}'.format(dept)
	response = requests.get(url)
	soup = BeautifulSoup(response.text, 'html.parser')
	courselist = soup.find_all('p', {'class': 'courseblocktitle'})
	courselist[:] = [unicodedata.normalize('NFKD', i.get_text()).split('.')[0].split(' ')[1] for i in courselist]
	return courselist
#pass this a list of strings of departments you want topic lists for. Returns list in form: [
#  {"dept": "ECE", "topics": {"2200": "Some scraped topic list for 2200 lorem ispum", "3600": "Some scraped topic list for 3600 lorem ispum" ... }},
#  {"dept": "MATH", "topics": {"2551": "Some scraped topic list for 2551 lorem ispum", "1551": "Some scraped topic list for 1551 lorem ispum" ... }}
#]
def TopicList(depts, level):
	topiclist = []
	for x in depts:
		temp = KnownSyllabiScraper(x)
		temp.availLinks(level)
		topiclist.append({'dept': x, 'topics': temp.parseTopics()})
	return topiclist
class KnownSyllabiScraper:
	def __init__(self, dept):
		self.dept = dept
		self.urlDict = {
			#websites with syllabi listings for CoE schools
			"ae": ["https://ae.gatech.edu/undergraduate-course-descriptions", "https://ae.gatech.edu/ae-graduate-courses"],
			"bmed": ["https://bme.gatech.edu/bme/4-year-plan", "https://www.bme.gatech.edu/bme/grad-course-offerings"],
			"isye": ["https://www.isye.gatech.edu/academics/bachelors/current-students/curriculum/courses", "https://www.isye.gatech.edu/academics/masters/ms-industrial-engineering/curriculum"],
			"chbe": ["https://www.chbe.gatech.edu/undergrad-curriculum", "https://www.chbe.gatech.edu/graduate-classes-offered"],
			"cee": None,
			"ece": ["https://www.ece.gatech.edu/courses/course_list", "https://www.ece.gatech.edu/courses/textbook_list"],
			# ece special case undergrad and grad, textbook list
			"mse": ["http://www.mse.gatech.edu/undergraduate-program/syllabi", "http://www.mse.gatech.edu/graduate/syllabi"],
			"me": ["http://www.me.gatech.edu/undergraduate/me-syllabi", "https://www.me.gatech.edu/graduate-course-offerings-course-number-and-frequency"],
			"nre": ["http://www.nre.gatech.edu/academics/nre/ug/syllabi", "http://www.nre.gatech.edu/academics/grad/nre/syllabi"],



			"biol": None,

			# Different format
			"math": ["https://math.gatech.edu/courses/math/{0}", None],


			"hts": ["https://hsoc.gatech.edu/undergraduate/courses/all", "https://hsoc.gatech.edu/graduate/courses"],

			# Econ has a weird filter system we need to work through
			"econ": ["https://econ.gatech.edu/courses", None],

			# Needs different link scraper for nested links
			"chem": ["https://chemistry.gatech.edu/academics/courses", "https://chemistry.gatech.edu/academics/courses"],

			"neur": None,

			"psyc": None,

			# They have a lot of github sites we might wanna take from
			"cs": None,

			"mgt": None,

			"acct": None,






		}

	def availLinks(self, level):
		#request relevant site for department
		levelId = {"undergrad": 0, "grad": 1}[level]
		response = requests.get(self.urlDict[self.dept][levelId])
		soup = BeautifulSoup(response.text, "html.parser")

		#get all course numbers for department
		allCourses = CourseList(self.dept, level)
		self.availCourses = soup.find_all('a', href=True)
		#print(self.availCourses) # Uncomment to check for VPN site error


		#extract dict of courses that 1. have a department course number as substring 2. have substring root url
		self.availCourses = {[z for z in allCourses if z in i['href']][0] : i['href'] for i in self.availCourses if any(j in i['href'] for j in allCourses)}
		#add pathing for absolute address to get full url
		for course, link in self.availCourses.items():
			if ("http" != link[0:4]): self.availCourses[course] = urljoin(self.urlDict[self.dept][levelId], link)
		self.availCourses = {course : url for (course, url) in self.availCourses.items() if urlparse(self.urlDict[self.dept][levelId]).netloc.replace("www.","") in url}
		return self.availCourses
		
	def downloadPDF(self, response, filename):
		# response = requests.get(url, verify = False)
		with open(filename + ".pdf", 'wb') as file:
			file.write(response.content)

	def downloadSite(self, response, course):
		if (response.status_code == 200):
			src = response.content
			soup = BeautifulSoup(src, 'lxml')
			output = str(soup)
			output = output[output.find("region-content block-count1") + 38:]
			output = output[:output.find('\n</div>\n</div>\n</div>') + 21]
			html = HTML(string=output)
			html.write_pdf('{0}/{1}{2}.pdf'.format(self.dept,self.dept, course))
		else:
			print("The syllabi page for " + self.dept + " " + course + " is not responding and thus a PDF was not created for it's syllabi.")



	def processSyllabi(self, course):
		response = requests.get(self.availCourses[course], verify = False)
		contentType = response.headers.get('content-type')
		if "application/pdf" in contentType:
			self.downloadPDF(response, self.dept + '/' + self.dept + course)
		elif "text/html" in contentType:
			self.downloadSite(response, course)
		else:
			print("The syllabi page for " + self.dept + " " + course + " is neither an HTML website nor a pdf thus a PDF was not created for it's syllabi.")

	def downloadDept(self):
		try:
			os.mkdir(self.dept)
		except:
			pass
		for course in self.availCourses:
			self.processSyllabi(course)
	def parsePDF(self, course):
		parsed_pdf = parser.from_file('{0}/{1}{2}.pdf'.format(self.dept, self.dept, course), xmlContent=False)
		pdf = parsed_pdf['content']
		pdfLower = pdf.lower()
		found = False
		keywords = ["topical outline", "topic"]
		counter = 0
		for word in keywords:
			counter = pdfLower.count(word)
			if counter > 0:
				keyword = word
				found = True
				break
		# reduces syllabus down to after the keyword
		if found:
			afterKeyWord = (pdf[pdfLower.find(keyword):])
			#print("found start") # Uncomment to print if topics are found
			# removes extra whitespace
			while(afterKeyWord.count("\n\n")>=1):
				afterKeyWord = afterKeyWord.replace("\n\n","\n")
			afterKeyWordLower = afterKeyWord.lower()
			endKeyWords = {"summary" : 1e10, "total" : 1e10, "learn" : 1e10, "course" : 1e10, "objective" : 1e10, "grading" : 1e10}
			endFound = False
			endCounter = 0
			for y in endKeyWords.keys():
				endCounter = afterKeyWordLower.count(y)
				if endCounter > 0:
					endFound = True
					endKeyWords[y] = afterKeyWordLower.find(y)
			if endFound:
				#print("end found in " + self.dept + course + "\n") # Uncomment to print if end is truncated
				output = afterKeyWord[:afterKeyWordLower.find(min(endKeyWords, key=endKeyWords.get))]
			else:
				output = afterKeyWord
				#print("end not found in " + self.dept + course + "\n") # Uncomment to print if end is truncated
			return(output)
		else:
			return("cannot find topics in " + self.dept + course + "\n")

	# Make work with math and meche		
	#**ONLY WORKS WITH ECE RIGHT NOW** grabs topic list directly from website.
	def parseSite(self, course):
		if (self.dept == "ece"):
			result = requests.get('https://www.ece.gatech.edu/courses/course_outline/{0}{1}'.format(self.dept.upper(), course))
			if (result.status_code == 200):
				src = result.content
				soup = BeautifulSoup(src, 'lxml')
				soup_string = str(soup)
				output = soup_string[soup_string.find("<dt><strong>Topical Outline"):]
				output = output[:output.find("</dd>") + 5]
				output = BeautifulSoup(output,"lxml").text
			else:
				output = "cannot find course topics"
		elif (self.dept == "me"):
			

			
		return output
	#returns a dictionary in the form {"2020": "[Topic list for 2020]", "2035": "[Topic list for 2035]"} to be used in TopicList method.
	def parseTopics(self):
		if(list(self.availCourses.values())[0][len(list(self.availCourses.values())[0])-4:] == '.pdf'):
			self.availTopics = self.availCourses
			for x in self.availCourses.keys():
				self.availTopics[x] = self.parseSite(x)
			return self.availTopics
		else:
			self.availTopics = self.availCourses
			for x in self.availCourses.keys():
				try:
					self.availTopics[x] = self.parsePDF(x)
				except:
					self.availTopics[x] = "PDF unavailable"
			return self.availTopics
#!/usr/bin/python
import sys, json, os, cgi, cgitb, logging, rfc3339
from datetime import datetime
from smtplib import SMTP
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


#enable CGI traceback and set up logging
cgitb.enable()
logging.basicConfig(filename='./log/JsonSendMail.log',level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
success_msg = {'success':'Yes','message':'Outage Information Email Sent.'}
error_msg = {'success':'No','message':'Email Failed to Send!'}
emailToDict = {"Long List":['taoli@cityofpasadena.net', 'ermoule@cityofpasadena.net', 'cfortich@cityofpasadena.net'], 
				"Short List":['taoli@cityofpasadena.net']}

# def convertJsDate(date_in):
	# #format and splice out seconds
	# date_processing = date_in.replace('T', '-').replace('Z','').replace(':', '-').split('-')[:-1]
	# date_processing = [int(v) for v in date_processing]
	# date_out = datetime(*date_processing).strftime("%y/%m/%d %H:%M")
	# return date_out
	
def convertRfc3339Date(date_in):
	epoch_time = rfc3339.strtotimestamp(date_in)
	return datetime.fromtimestamp(epoch_time).strftime('%Y/%m/%d %H:%M')

def checkJSONParam(json_data, param_list):
	check_flag = True
	for param in param_list:
		if not json_data.has_key(param):
			check_flag = False
			break
	return check_flag

#postData = {"incidentRadius":0.2,"incidentTime":"2016-09-21T15:40:19.029Z","estimateDowntime":2,"recipientList":"Long List","incidentResolution":"No","incidentDescription":"dd"}
#logging.debug(str(postdict['incidentRadius']))
# Do something with 'myjson' object

try:
	#get content length header from cgi environment and read stdin or POST into dictionary 
	readLength = int(os.environ.get('CONTENT_LENGTH', 0))
	postData = sys.stdin.read(readLength)
	postDataDict = json.loads(postData)
	#log record on delete
	if postDataDict['incidentResolution'] == 'Delete':
		logging.debug("Following Record Was Deleted From Database: \n" + str(postDataDict))
	#check all fields present
	if not checkJSONParam(postDataDict, ('incidentRadius', 'incidentTime', 'estimateDowntime', 'recipientList', 'editorLogin', 'incidentResolution', 'incidentDescription')):
		raise Exception("Missing Form Parameters")
	incidentRadius = postDataDict['incidentRadius']
	incidentTime = convertRfc3339Date(postDataDict['incidentTime'])
	estimateDowntime = postDataDict['estimateDowntime']
	recipientList = postDataDict['recipientList']
	resolutionLookup = {'Yes':'<font color="green">Incident Resolved</font>', 'No':'<font color="blue">Resolution Pending</font>', 'Delete':'<font color="red">Incident Retracted</font>'}
	incidentResolution = resolutionLookup[postDataDict['incidentResolution']]
	editorLogin = postDataDict['editorLogin']
	incidentDescription = cgi.escape(postDataDict['incidentDescription'])
	sender = 'taoli@cityofpasadena.net'
	receivers = emailToDict[recipientList]
	cssStyle = """
		th {
			vertical-align: top;
			text-align:right;
			font-weight: normal
		}
	"""
	mail_text = """
	Important Information Regarding Water Outage!
	Resolution: %s
	Time: %s
	Radius: %s mi
	Estimate Downtime: %s hr
	Editor Login: %s
	Description: %s
	""" % (incidentResolution, incidentTime, incidentRadius, estimateDowntime, editorLogin, incidentDescription)
	mail_HTML = """\
	<html>
	 <head>
	 	<style type="text/css">
		%s 
		</style>
	 </head>
	 <body>
	   <h2>Important Information Regarding Water Outage</h2>
	   <p><u>details as follow:</u><br />
	   <table>
			<tr>
			  <th scope="row">Resolution:</th> 
			  <td>%s</td>
		    </tr>
		    <tr>
			  <th scope="row">Time:</th>
			  <td>%s</td>
		    </tr>
		    <tr>
			  <th scope="row">Radius:</th> 
			  <td>%s mi</td>
		    </tr>
			<tr>
			  <th scope="row">Estimate Downtime:</th> 
			  <td>%s hr</td>
		    </tr>
			<tr>
			  <th scope="row">Editor Login:</th> 
			  <td>%s</td>
		    </tr>
			<tr>
				<th scope="row">Description:</th> 
				<td>%s</td>
			<tr>
		</table>
	   </p>
	 </body>
	</html>
	""" % (cssStyle, incidentResolution, incidentTime, incidentRadius, estimateDowntime, editorLogin, incidentDescription.replace('\n', '<br />'))
	part1 = MIMEText(mail_text, 'plain')
	part2 = MIMEText(mail_HTML, 'html')

	smtpObj = SMTP('smtp.ci.pasadena.ca.us', 25)
	my_mail = MIMEMultipart('alternative')
	my_mail['From'] = 'svrwp-gis-sw-d@cityofpasadena.net'
	my_mail['To'] = ", ".join(receivers)
	my_mail['X-Priority'] = '2'
	my_mail['Subject'] = 'Important Water Outage Information'
	my_mail.attach(part1)
	my_mail.attach(part2)  
	smtpObj.sendmail(sender, receivers, my_mail.as_string())
	success_json = json.dumps(success_msg)
	print "Status: 200 OK"
	print 'Content-Type: application/json'
	print "Content-Length: %d" % (len(success_json))
	print ""
	print success_json
except Exception as err:
	logging.error(err)
	error_json = json.dumps(error_msg)
	print "Status: 200 OK"
	print 'Content-Type: application/json'
	print "Content-Length: %d" % (len(error_json))
	print ""
	print error_json
	
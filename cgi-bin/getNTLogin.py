# Configure Impersonate User to True, disallow annoymous login, get Remote_addr and Remote_user from CGI environment variable.
# To enable logging in log folder under wwwroot, disable permission inheritance and grant write permission to Everyone (role)
# Do not use Windows Management Instrument (wmi), it require application pool identity to run as a network admin
import cgi, cgitb, os, logging, json
cgitb.enable()
logging.basicConfig(filename='./log/getNTLogin.log',level=logging.DEBUG)
login_info = {}
try:
	remote_addr = cgi.escape(os.environ["REMOTE_ADDR"])
	login_info['remote_addr'] = remote_addr
	#logging.debug(remote_addr)
	remote_user = (cgi.escape(os.environ["REMOTE_USER"])).split("\\")[-1]
	login_info['remote_user'] = remote_user
	#logging.debug(remote_user)
	success_json = json.dumps(login_info)
	# management_instrument = wmi.WMI(remote_addr)
	# for process in management_instrument.Win32_Process(name='explorer.exe'):
		# logging.debug(process.GetOwner())
	print "Status: 200 OK"
	print 'Content-Type: application/json'
	print "Content-Length: %d" % (len(success_json))
	print ""
	print success_json
except Exception as err:
	logging.error(err)
	error_json = json.dumps({'remote_addr':'0.0.0.0','remote_user':'Unknown User'})
	print "Status: 200 OK"
	print 'Content-Type: application/json'
	print "Content-Length: %d" % (len(error_json))
	print ""
	print error_json
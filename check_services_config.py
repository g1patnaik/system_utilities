'''
name  - A script name (Mandatory)
script - Full script path (Mandatory)
gap_on_ok - Time in seconds to check the script again on success
gap_on_fail - Time in seconds to check the script on failure
max_attempt - Maximum number of attempts to make before sending alert
Timeout - Timeout to fail if check script doesn't respond
notify - Boolean to enable or disable alerts
notify_list - Send alert to these mail id specified in list format
'''

# Chaange defaults here
default_dict = {
  'gap_on_ok' : 60,
  'max_attempt' : 3,
  'gap_on_fail' : 10,
  'timeout' : 10,
  'notify' : True,
  'notify_list' : ['a@abc.com,b@abc.com'],
  'sender' : 'abc@123.com'
}

dictlist =  [
{
  'name' : 'something-1',
  'script' : '/somedir/check_something-1.sh'
},
{
  'name' : 'something-2',
  'script' : '/somedir/check_something-2.sh',
}
]

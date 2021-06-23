#!/bin/python3
import subprocess
import sys
from time import sleep
from datetime import datetime, timedelta
import logging
import argparse

from send_mail import sendMail


class CheckService:
  "Service check Class"

  def __init__(self,name,script,gap_on_ok=60,max_attempt=3,gap_on_fail=30,timeout=10,notify=False,notify_list=None,sender=None):
     self.notify = notify
     self.attempt = 0
     self.warn_alert = True
     self.ok_alert = False
     self.max_attempt = max_attempt
     self.script = script
     self.gap_on_fail = gap_on_fail
     self.timeout = timeout
     self.notify_list = notify_list
     self.sender = sender
     self.name = name
     self.nextcheck = datetime.now()
     logging.debug(f"Next check for {self.name} is after {self.nextcheck}")
     self.gap_on_ok = gap_on_ok

  def run(self):
     if (datetime.now() < self.nextcheck):
       return
     returncode, out, err = run_check(self.script,self.timeout)
     logging.debug(f'''
{self.name} returncode
{returncode}
{self.name} stdout:
{out.decode('utf-8')}
{self.name} stderr:
{err.decode('utf-8')}
''')
     if (returncode != 0) :
       if not self.warn_alert:
         logging.warning(f"{self.name} is not recovered. Alert is already sent")
       elif ( self.notify and self.attempt == self.max_attempt ):
         logging.error(f"{self.name} non-zero return code and max tries reached. Sending notification to {self.notify_list}")
         subject = f'{self.name} service check fail'
         message = f'''
{self.name} - service check returned non-zero return code and max tries are reached
{out.decode('utf-8')}.
{err.decode('utf-8')}
'''
         sendMail(sender,self.notify_list,subject,message)
         self.warn_alert = False
         self.ok_alert = True
       else:
         self.attempt+=1
         logging.error(f"{self.name} non-zero return code. Checking again after {self.gap_on_fail} seconds")
       self.nextcheck = datetime.now() + timedelta(seconds=self.gap_on_fail)
       logging.debug(f"Next check for {self.name} is after {self.nextcheck}")
     else:
       logging.info(f"{self.name} is OK")
       if self.notify:
         if self.ok_alert:
           subject = f'{self.name} service check OK'
           message = f'''
{self.name} - service is recovered
{out.decode('utf-8')}
{err.decode('utf-8')}
'''
           sendMail(sender,self.notify_list,subject,message)
         self.ok_alert = False
       self.attempt = 0
       self.warn_alert = True
       self.nextcheck = datetime.now() + timedelta(seconds=self.gap_on_ok)
       logging.debug(f"Next check for {self.name} is after {self.nextcheck}")


def run_check(script,timeout):
  try:
    result = subprocess.run(script,timeout=timeout,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    return result.returncode, result.stdout, result.stderr
  except FileNotFoundError:
    return 255, b"", b"Check script not found"
  except:
    return 2, e.stdout, e.stderr

def load_config():
   import check_services_config as cfg
   from collections import ChainMap
   cfg.dictlist = [ChainMap(dictitem, cfg.default_dict) for dictitem in cfg.dictlist]
   load_config.services = []
   for dictitem in cfg.dictlist:
      load_config.services.append(CheckService(**dictitem))


def main(argv):
    arg_parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    arg_parser.add_argument('--loglevel', default='INFO', required=False, help='Logging Level', type=str, choices=('INFO','DEBUG','ERROR','WARN'))
    args = arg_parser.parse_args(argv)

    numeric_level = getattr(logging, args.loglevel.upper(), 'INFO')
    if not isinstance(numeric_level, int):
       raise ValueError('Invalid log level: %s' % loglevel)
    logging.basicConfig(
      format='%(asctime)s %(levelname)-8s %(message)s',
      level=numeric_level,
      datefmt='%Y-%m-%d %H:%M:%S')

    load_config()
    while True:
      for service in load_config.services:
        logging.debug(f"checking {service.name}")
        service.run()
        logging.debug(f"Sleep for 30 seconds")
      sleep(30)

def sigterm_handler(_signo, _stack_frame):
    sys.exit(0)

#TODO
'''
def sigusr1_handler(_signo, _stack_frame):
    print("Handling SIGUSR1 signal")
    load_config()
'''

import signal
signal.signal(signal.SIGINT, sigterm_handler)
signal.signal(signal.SIGTERM, sigterm_handler)
#signal.signal(signal.SIGUSR1, sigusr1_handler)

if __name__ == "__main__":
    try:
      main(sys.argv[1:])
    finally:
      print("Bye")

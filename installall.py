#!/usr/bin/python

import subprocess

subprocess.call("./controllerScript.py", shell=True)
subprocess.call("./neutronScript.py", shell=True)
subprocess.call("./computeScript.py", shell=True)
subprocess.call("./vpnaas.sh", shell=True) #httpAction.py is invoked from within vpnaas.sh

#subprocess.call("python httpAction.py", shell=True)
#subprocess.call("./vpnaas.sh", shell=True)

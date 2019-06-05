#/bin/sh

if [ -z "$JOBID" ]; then 
  echo "Script is supposed to run in beaker environment, exittng now"; 1>&2
  exit 1;
fi

# This program has dependensies on python3-setuptools
# In RHEL-7 we need to install packages: python34  and python34-setuptools
# In RHEL-8 we need to install packages: python3-setuptools
# Line below tries to install RHEL-7 packages and if fails it will try to install RHEL-8 packages. If at least one of installation is succesfull
# it runs setup script which installs this program.
which sync_client &> /dev/null || ( (yum -y install python34 python34-setuptools || yum -y install python3-setuptools) && python3 ./setup.py install)
./sync_client --job $JOBID $SYNC_ARGS && rhts-report-result $TEST PASS /dev/null && exit 0

# 42 is returned if no functionvariables are specified to sync_client
# it is not reason to FAIL task
if [ "$?" == "42" ]; then
	rhts-report-result $TEST PASS /dev/null && exit 0
fi

rhts-report-result $TEST FAIL /dev/null && exit 1

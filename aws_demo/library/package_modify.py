#!/usr/bin/python

from ansible.module_utils.basic import *
import sys
import subprocess

DOCUMENTATION = r'''
  description: Removing single or multiple package using regex
  options:
    via_regex:
      This will take a regex which is going to be the package name or close to package regex The parameters are case insensitive.

    all_found_uninstall:
      By defualt this value is set to false but if set to true then all the package found within given regex will be uninstalled
'''

EXAMPLES = r'''
  - name: Delete package
    package_modify:
       via_regex: 'package*'
     
  - name: Delete any package that has td in it
    package_modify:
       via_regex: 'td'
       all_found_uninstall: true
      
'''

def rpm_finding_package(via_regex):
    re_package = []
    cmd = ""
    if sys.version_info[0] == int(2) and sys.version_info[1] < int(7):
      cmd = "rpm -qa | grep -i '%s'"% via_regex
    else:
      cmd = "rpm -qa | grep -i {}".format(via_regex)
    result = subprocess.Popen(cmd,shell=True,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    pkg = result.stdout.readlines(-1)
    err = result.stderr.readlines(-1)
 
    for p in pkg:
        re_package.append(p.rstrip())

    return re_package,err

def rpm_package_removing(pkg,all_found_uninstall):
    cmd2 = ""
    modifying = []
    rpkg = []
    rerr = []
    if all_found_uninstall:
        # python3 requires decoding to be done manually
        if sys.version_info[0] == int(3):
            for i in pkg:
                modifying.append(i.decode('utf-8'))

        # removing newlines and spaces
        modifying = [i.strip() for i in modifying]

        for packages in modifying:
            if sys.version_info[0] == int(2) and sys.version_info[1] < int(7):
              cmd2 = "rpm -e  '%s'"% packages
            else:
              cmd2 = "rpm -e {}".format(packages)
            result = subprocess.Popen(cmd2,shell=True,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            outpkg= result.stdout.readlines(-1)
            outerr = result.stderr.readlines(-1)
            for i in outpkg:
              rpkg.append(i)
            for j in outerr:
              rerr.append(j)

    elif not all_found_uninstall:     
        if sys.version_info[0] == int(2) and sys.version_info[1] < int(7):
          cmd2 = "rpm -e  '%s'"% pkg[0]
        else:
          cmd2 = "rpm -e {}".format(pkg[0].decode('utf-8'))
        result = subprocess.Popen(cmd2,shell=True,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        outpkg = result.stdout.readlines(-1)
        outerr = result.stderr.readlines(-1)
        for i in outpkg:
          rpkg.append(i)
        for j in outerr:
          rerr.append(j)

    return rpkg,rerr


def main():

    Result = None
    changed = False
    fields=dict(
        via_regex=dict(required=True, type='str'),
        all_found_uninstall=dict(required=False, default=False,type= bool,choices=[True,False])
    )


    # Ansible module is defined here 
    module = AnsibleModule(
        argument_spec=fields,
        supports_check_mode=True,
    )

    via_regex = module.params["via_regex"]
    all_found_uninstall = module.params["all_found_uninstall"]

    result = None
    changed = False
    msg=""

    fnd_package,error = rpm_finding_package(via_regex)
    if len(error) >= 1:
        result = error
        changed = False
        module.fail_json(msg=error)

    elif len(fnd_package) > 1 and all_found_uninstall == False:
        result = fnd_package
        changed = False
        msg = "Multiple packge found while the all_found_uninstall is set to false"

    elif not len(fnd_package):
        result = None
        changed = False
        msg="No package found or uninstalled already"

    elif fnd_package:
    
        result_output,error_removing = rpm_package_removing(fnd_package, all_found_uninstall)

        if error_removing:
            result = error
            changed = False
            module.fail_json(msg=error_removing)
    
        elif result_output:
            result = result
            changed = True
            msg="uninstalled successfully"

    module.exit_json(changed=changed, msg=msg,result=result)

if __name__ == "__main__":
    main()
#!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule
import requests
import os
import subprocess

def download_file(url, dest):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Check for HTTP errors

        with open(dest, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        return True, None
    except Exception as e:
        return False, str(e)

def run_script(script_path):
    try:
        result = subprocess.run([script_path], check=True, shell=True, capture_output=True, text=True)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

def main():
    module = AnsibleModule(
        argument_spec=dict(
            url=dict(type='str', required=True),
            dest=dict(type='str', required=True),
            mode=dict(type='str', default='0755')
        ),
        supports_check_mode=True
    )

    url = module.params['url']
    dest = module.params['dest']
    mode = module.params['mode']

    # Ensure the destination directory exists
    dest_dir = os.path.dirname(dest)
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    # Download the file
    success, error_message = download_file(url, dest)
    if not success:
        module.fail_json(msg='Failed to download file', error=error_message)

    # Set file permissions
    try:
        os.chmod(dest, int(mode, 8))
    except Exception as e:
        module.fail_json(msg='Failed to set file permissions', error=str(e))

    # Run the script
    success, output_or_error = run_script(dest)
    if not success:
        module.fail_json(msg='Failed to execute script', error=output_or_error)

    module.exit_json(changed=True, msg='Script downloaded and executed successfully', output=output_or_error)

if __name__ == '__main__':
    main()

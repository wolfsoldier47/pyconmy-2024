#pip install boto3
#pip install ansible
#ansible-galaxy colelction install community.general 
#brew install terraform


ansible-playbook playbook.yml -e "plan=destroy" --ask-vault-pass

ansible-playbook playbook2.yml -i inventory.aws_ec2.yml
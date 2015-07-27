# Demo Environment Ansible Scripts

These are the scripts used to stand up your own environment running the demo from the
[2015 JBoss Middleware Keynote](https://www.youtube.com/watch?v=wWNVpFibayA) at Red Hat Summit.

## Prerequisites

- An AWS account with permissions to do the following:
  - Create and modify a VPC
  - Create and modify Security Groups
  - Create and modify route53 entries
  - Craete and modify EC2 instances
- AWS credentials may be specified either through the `AWS_ACCESS_KEY_ID` and
    `AWS_SECRET_ACCESS_KEY` env variables or using any of the environment
    variables/configs supported by
    [boto](http://boto.readthedocs.org/en/latest/boto_config_tut.html)
- 2 pre-created route53 host zones
  - 1 for host entries that are assigned to each created instance
  - 1 for the application domain (a wildcard entry is created that maps to the router)
- An SSH keypair in mind, with the key exported via ssh-add

## Requirements

- [Ansible](https://github.com/ansible/ansible) version 1.9.1 or greater
- The master branch of
    [openshift/openshift-ansible](https://github.com/openshift/openshift-ansible)
    is expected to be a sibling repo to the demo-ansible repo

  ```
  git clone https://github.com/2015-Middleware-Keynote/demo-ansible.git
  git clone https://github.com/openshift/openshift-ansible.git
  ```

## Standing up a new Environment

```
cd demo-ansible
ansible-playbook -i inventory/aws/hosts playbooks/openshift_setup.yml
```

# Demo Environment Ansible Scripts

These are the scripts used to stand up your own environment running the demo from the
[2015 JBoss Middleware Keynote](https://www.youtube.com/watch?v=wWNVpFibayA) at Red Hat Summit.

## Prerequisites

- An AWS account with permissions to do the following:
  - Create and modify a VPC (A VPC is created for each cluster-id)
  - Create and modify Security Groups (2 security groups are created for each
    cluster-id, one for masters and one for nodes)
  - Create and modify route53 entries (Route 53 entries are added to the
    hosted zone specified by r53-zone for each ec2 instance created as well as
    a wildcard dns entry for router)
  - Craete and modify EC2 instances
- AWS credentials may be specified either through the `AWS_ACCESS_KEY_ID` and
    `AWS_SECRET_ACCESS_KEY` env variables or using any of the environment
    variables/configs supported by
    [boto](http://boto.readthedocs.org/en/latest/boto_config_tut.html)
- A pre-created route53
    [public hosted zone](http://docs.aws.amazon.com/Route53/latest/DeveloperGuide/CreatingHostedZone.html)
- A pre-created ec2 keypair
  - You will need to specify the name of this keypair when running the
      environment creation script
  - You will also need to add the private key to your ssh agent: `ssh-add <path to key file>`

## Requirements

- [Ansible](https://github.com/ansible/ansible) version 1.9.1 or greater
- [Click](https://github.com/mitsuhiko/click) version 3.0 or greater
  - Available in Fedora and EPEL channels as python-click
- The master branch of
    [openshift/openshift-ansible](https://github.com/openshift/openshift-ansible)
    is expected to be a sibling repo to the demo-ansible repo

  ```
  git clone https://github.com/2015-Middleware-Keynote/demo-ansible.git
  git clone https://github.com/openshift/openshift-ansible.git
  ```

## Standing up a new Environment
List the options for run.py:
```
cd demo-ansible
./run.py --help
```


Stand up an environment using the defaults. run.py will prompt for Rhsm user, Rhsm password and route53 hosted zone
```
./run.py
```

Stand up an environment without being prompted for confirmation and overriding
the cluster id, environment size, and keypair:
```
./run.py --no-confirm --cluster-id my_cluster --env-size medium --keypair my_keypair \
--r53-zone my.hosted.domain --rhsm-user my_redhat_user --rhsm-pass my_redhat_pass
```

After the run has completed the openshift web console will be available at
`https://openshift-master.<cluster id>.<r53 zone>` and routes created for
applications will default to `<app name>.<project name>.<cluster id>.<r53 zone>`

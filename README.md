# OpenShift 3 Demo Environment Provisioner
These Ansible scripts were originally created to stand up an environment running the demo from the
[2015 JBoss Middleware Keynote](https://www.youtube.com/watch?v=wWNVpFibayA) at Red Hat Summit.

At this point, this script repository serves two purposes:

1. Creating an environment that will pre-build and pre-configure the Hexboard
application for you to be able to conduct a scale-out demo

2. Creating an environment suitable for running a workshop with many users

## Overview
These scripts stand up an environment running on [Amazon Web
Services](https://aws.amazon.com). They use CloudFormations, EC2, VPC, Route 53,
and IAM services within AWS. They provision several RHEL7-based servers that are
participating in an HA [OpenShift 3](https://openshift.com/enterprise)
environment that has persistent storage for its infrastructure components.

Additionally, the scripts set up OpenShift's metrics and logging aggregation
services.

The scripts can create workshop users, too.

## Prerequisites
In order to use these scripts, you will need to set a few things up.

- An AWS IAM account with the following permissions:
  - Policies can be defined for Users, Groups or Roles
  - Navigate to: AWS Dashboard -> Identity & Access Management -> Select Users or Groups or Roles -> Permissions -> Inline Policies -> Create Policy -> Custom Policy
    - Policy Name: openshift (your preference)
    - Policy Document:
```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "Stmt1459269951000",
            "Effect": "Allow",
            "Action": [
                "cloudformation:*",
                "iam:*",
                "route53:*",
                "elasticloadbalancing:*",
                "ec2:*",
                "cloudwatch:*",
                "autoscaling:*"
            ],
            "Resource": [
                "*"
            ]
        }
    ]
}
```
  Finer-grained permissions are possible, and pull requests are welcome.

- AWS credentials for the account above must be exported through the
    `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` environment variables in
    your shell.
- A route53 [public hosted
    zone](http://docs.aws.amazon.com/Route53/latest/DeveloperGuide/CreatingHostedZone.html)
    is required for the scripts to create the various DNS entries for the
    resources it creates.
- An EC2 SSH keypair should be created in advance and you should save the key
    file to your system.
- A Red Hat Customer Portal account that has appropriate OpenShift subscriptions
    - Red Hat employee subscriptions can be used
- Instead of RHCP and RHSM, you may use certificate-based software repositories.
    This feature is designed for Red Hat internal use only.

## Software Requirements
### Packaged Software
- [Python](https://www.python.org) version 2.7.x (3.x untested and may not work)
- [Python Click](https://github.com/mitsuhiko/click) version 4.0 or greater
- [Python Boto](http://docs.pythonboto.org) version 2.38.0 or greater
- [Ansible](https://github.com/ansible/ansible) version 1.9.4

Python and the Python dependencies may be installed via your OS' package manager
(eg: python-click on Fedora/CentOS/RHEL) or via
[pip](https://pypi.python.org/pypi/pip). [Python
virtualenv](https://pypi.python.org/pypi/virtualenv) can also work.

### GitHub Repositories
While the demo-ansible scripts are contained in a GitHub repository, the rest of
the OpenShift installer lives in a separate repository. You will need both of
them, and very specific versions of each.

- `demo-ansible`
    - [2015-Middleware-Keynote/demo-ansible](https://github.com/2015-Middleware-Keynote/demo-ansible)
    - You will want to use `master` until we implement tags on this repository
    - You will want to check out tag `demo-ansible-2.0.0`
- `openshift-ansible`
    - [openshift/openshift-ansible](https://github.com/openshift/openshift-ansible)
    - You will want to check out tag `openshift-ansible-3.0.47-6`

The folders for these repositories are expected to live in the same
subdirectory. An example tree structure is below:
```
/home/user/ansible-scripts
|-- demo-ansible
|-- openshift-ansible
```

In this case, you could do something like the following:
```
cd /home/user/ansible-scripts
git clone https://github.com/2015-Middleware-Keynote/demo-ansible.git
cd demo-ansible
git checkout demo-ansible-2.0.0
cd ..
git clone https://github.com/openshift/openshift-ansible.git
cd openshift-ansible
git checkout openshift-ansible-3.0.47-6
```

## Usage
### Export the EC2 Credentials
You will need to export your EC2 credentials before attempting to use the
scripts:
```
export AWS_ACCESS_KEY_ID=foo
export AWS_SECRET_ACCESS_KEY=bar
```

### Add the SSH Key to the SSH Agent
You will need to add the private key to your SSH agent: 
```
ssh-add <path to key file>
```

### `run.py`
There is a Python script, run.py, that takes options and calls Ansible to run
the various playbooks.

#### Defaults
List the options for run.py:
```
cd /path/to/demo-ansible
./run.py --help
```

The options will show you the various defaults. Of special note is the Amazon
EC2 AMI ID as well as the region. Here is a list of the AMIs and region IDs that
should be used:

    | AMI           | Amazon Region  |
    | ---           | ---            |
    | ami-2051294a* | us-east-1*     |
    | ami-d1315fb1  | us-west-1      |
    | ami-775e4f16  | us-west-2      |
    | ami-8b8c57f8  | eu-west-1      |
    | ami-875042eb  | eu-central-1   |
    | ami-0dd8f963  | ap-northeast-1 |
    | ami-44db152a  | ap-northeast-2 |
    | ami-3f03c55c  | ap-southeast-1 |
    | ami-e0c19f83  | ap-southeast-2 |
    | ami-27b3094b  | sa-east-1      |
    * is default

Most of the defaults are sensible for a small environment. To use them, simply
execute `run.py` by itself:
```
./run.py
```

You will be prompted for a Route 53 zone to place DNS entries into, and a Red
Hat customer portal login and password. It is expected that your SSH keypair
name is "default".

#### Other Examples
Stand up an environment without being prompted for confirmation and overriding
the cluster id, and keypair:
```
./run.py --no-confirm --cluster-id my_cluster --keypair my_keypair \
--r53-zone my.hosted.domain --rhsm-user my_redhat_user --rhsm-pass my_redhat_pass
```

## Access the Environment
If the installation and configuration completes successfully, you will see
something like the following:
```
Your cluster provisioned successfully. The console is available at https://openshift.<clustername>.<route53dnszone>:443
You can SSH into a master using the same SSH key with: ssh -i /path/to/key.pem openshift@openshift-master.<clustername>.<route53dnszone>
```

## Cleanup
`run.py` has a `--cleanup` option that can be used to delete all of the
resources it created. You will need to specify all of the same options that you
used to create your environment when you use `--cleanup`.

## Troubleshooting
You may see various errors from Ansible during the installation. These are
normal. Unless you see the word `FATAL` or `aborting`, there is nothing to worry
about.

### Failed Installation and Configuration
#### Cloudformation
For whatever reason, on occasion the Cloudformation template will fail to
provision correctly. There is no way to recover from this. Go into the AWS
console and find the Cloudformation stack and delete it. Start over.

#### Docker
There is a known issue where sometimes EC2's underlying storage subsystem is
unstable and `docker-storage-setup` will fail to run correctly because the
underlying LVM setup fails. This will manifest as a `FATAL` Ansible error where
the Docker daemon fails to start.

While re-running `run.py` with the same options can work, the resulting
environment has some nodes with a non-optimal Docker configuration.

If you encounter this particular error, it is adviseable to delete everything
and try again.

#### Other Errors
Generally, Ansible is pretty forgiving about other errors. If you have another
un-listed error, simply execute `run.py` again with the same exact options.

### Failed Cleanup
#### Cloudformation
On occasion the Cloudformation stack will fail to delete properly. Simply go
into the AWS console and find the Cloudformation stack and delete it.

#!/usr/bin/python

import click
import os
import sys

env_sizes = {'tiny': 1,
             'xsmall': 2,
             'small': 3,
             'medium': 5,
             'large': 10,
             'xlarge': 20
            }


@click.command()
@click.option('--cluster-id', default='demo', show_default=True,
              help='cluster identifier (used for assigning ec2 tags, naming security groups, and is used as a subdomain of the r53-zone for environment dns entries')
@click.option('--env-size', type=click.Choice(env_sizes),
              default='tiny', help='Environment size',
              show_default=True)
@click.option('--region', default='us-east-1', help='ec2 region',
              show_default=True)
@click.option('--ami', default='ami-12663b7a', help='ec2 ami',
              show_default=True)
@click.option('--master-instance-type', default='m4.large', help='ec2 instance type',
              show_default=True)
@click.option('--infra-instance-type', default='m4.large', help='ec2 instance type',
              show_default=True)
@click.option('--node-instance-type', default='m4.large', help='ec2 instance type',
              show_default=True)
@click.option('--keypair', default='default', help='ec2 keypair name',
              show_default=True)
@click.option('--r53-zone', prompt=True,
              help='route53 hosted zone (must be pre-configured)')
@click.option('--app-dns-prefix', default='apps', help='application dns prefix',
              show_default=True)
@click.option('--rhsm-user', prompt=True, help='Red Hat Subscription Management User')
@click.option('--rhsm-pass', prompt=True, hide_input=True,
              help='Red Hat Subscription Management Password')
@click.option('--no-confirm', is_flag=True,
              help='Skip confirmation prompt')
@click.help_option('--help', '-h')
@click.option('-v', '--verbose', count=True)

def launch_demo_env(env_size=None, region=None, ami=None, no_confirm=False,
                    master_instance_type=None, node_instance_type=None,
                    infra_instance_type=None, keypair=None, r53_zone=None,
                    cluster_id=None, app_dns_prefix=None, rhsm_user=None,
                    rhsm_pass=None, verbose=0):
    click.echo('Configured values:')
    click.echo('\tcluster_id: %s' % cluster_id)
    click.echo('\tenv_size: %s' % env_size)
    click.echo('\tregion: %s' % region)
    click.echo('\tami: %s' % ami)
    click.echo('\tmaster instance_type: %s' % master_instance_type)
    click.echo('\tnode_instance_type: %s' % node_instance_type)
    click.echo('\tinfra_instance_type: %s' % infra_instance_type)
    click.echo('\tkeypair: %s' % keypair)
    click.echo('\tr53_zone: %s' % r53_zone)
    click.echo('\tapp_dns_prefix: %s' % app_dns_prefix)
    click.echo('\trhsm_user: %s' % rhsm_user)
    click.echo('\trhsm_pass: *******')

    host_zone="%s.%s" % (cluster_id, r53_zone)
    wildcard_zone="%s.%s.%s" % (app_dns_prefix, cluster_id, r53_zone)

    click.echo('Host DNS entries will be created under the %s domain' % host_zone)
    click.echo('Application wildcard zone for this env will be %s' % wildcard_zone)

    if not no_confirm and not click.confirm('Continue using these values?'):
        sys.exit(0)

    # TODO: refresh the inventory cache to prevent stale hosts from
    # interferring with re-running
    command='inventory/aws/hosts/ec2.py --refresh-cache'
    os.system(command)

    command='ansible-playbook -i inventory/aws/hosts -e \'cluster_id=%s ec2_region=%s ec2_image=%s ec2_keypair=%s ec2_master_instance_type=%s ec2_infra_instance_type=%s ec2_node_instance_type=%s r53_zone=%s r53_host_zone=%s r53_wildcard_zone=%s num_app_nodes=%s hexboard_size=%s rhsm_user=%s rhsm_pass=%s\' playbooks/openshift_setup.yml' % (cluster_id, region, ami, keypair, master_instance_type, infra_instance_type, node_instance_type, r53_zone, host_zone, wildcard_zone, env_sizes[env_size], env_size, rhsm_user, rhsm_pass)

    if verbose > 0:
        command += " -" + "".join(['v']*verbose)

    #click.echo('\n\nRunning command: %s' % command)
    return os.system(command)

if __name__ == '__main__':
    launch_demo_env(auto_envvar_prefix='OSE_DEMO')

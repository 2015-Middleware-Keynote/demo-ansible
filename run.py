#!/usr/bin/env python
# vim: sw=2 ts=2

import click
import os
import sys

hexboard_sizes = ['tiny', 'xsmall', 'small', 'medium', 'large', 'xlarge']

@click.command()

### Cluster options
@click.option('--cluster-id', default='demo', show_default=True,
              help='Cluster identifier (used for prefixing/naming various items created in AWS')
@click.option('--num-nodes', type=click.INT, default=1, show_default=True,
              help='Number of application nodes')
@click.option('--num-infra', type=click.IntRange(1,3), default=1,
              show_default=True, help='Number of infrastructure nodes')
@click.option('--hexboard-size', type=click.Choice(hexboard_sizes),
              help='Override Hexboard size calculation (tiny=32, xsmall=64, small=108, medium=266, large=512, xlarge=1026)',
              show_default=True)
@click.option('--console-port', default='443', type=click.IntRange(1,65535), help='OpenShift web console port',
              show_default=True)
@click.option('--api-port', default='443', type=click.IntRange(1,65535), help='OpenShift API port',
              show_default=True)
@click.option('--deployment-type', default='openshift-enterprise', help='openshift deployment type',
              show_default=True)
@click.option('--default-password', default='openshift3',
              help='password for all users', show_default=True)

### Smoke test options
@click.option('--run-smoke-tests', is_flag=True, help='Run workshop smoke tests')
@click.option('--num-smoke-test-users', default=5, type=click.INT,
              help='Number of smoke test users', show_default=True)
@click.option('--run-only-smoke-tests', is_flag=True, help='Run only the workshop smoke tests')

### AWS/EC2 options
@click.option('--region', default='us-east-1', help='ec2 region',
              show_default=True)
@click.option('--ami', default='ami-2051294a', help='ec2 ami',
              show_default=True)
@click.option('--master-instance-type', default='m4.large', help='ec2 instance type',
              show_default=True)
@click.option('--infra-instance-type', default='m4.2xlarge', help='ec2 instance type',
              show_default=True)
@click.option('--node-instance-type', default='m4.large', help='ec2 instance type',
              show_default=True)
@click.option('--keypair', default='default', help='ec2 keypair name',
              show_default=True)

### DNS options
@click.option('--r53-zone', help='route53 hosted zone (must be pre-configured)')
@click.option('--app-dns-prefix', default='apps', help='application dns prefix',
              show_default=True)

### Subscription and Software options
@click.option('--package-version', help='OpenShift Package version (eg: 3.2.0.46)',
              show_default=True, default='3.2.0.46')
@click.option('--rhsm-user', help='Red Hat Subscription Management User')
@click.option('--rhsm-pass', help='Red Hat Subscription Management Password',
                hide_input=True,)
@click.option('--skip-subscription-management', is_flag=True,
              help='Skip subscription management steps')
@click.option('--use-certificate-repos', is_flag=True,
              help='Uses certificate-based yum repositories for the AOS content. Requires providing paths to local certificate key and pem files.')
@click.option('--aos-repo', help='An alternate URL to locate software')
@click.option('--prerelease', help='If using prerelease software, set to true',
              show_default=True, default=False, is_flag=True)
@click.option('--kerberos-user', help='Kerberos userid (eg: jsmith) for use with --prerelease')
@click.option('--kerberos-token', help='Token to go with the kerberos user for use with --prerelease')
@click.option('--registry-url', help='A URL for an alternate Docker registry for dockerized components of OpenShift',
              show_default=True, default='registry.access.redhat.com/openshift3/ose-${component}:${version}')

### Miscellaneous options
@click.option('--no-confirm', is_flag=True,
              help='Skip confirmation prompt')
@click.option('--debug-playbook',
              help='Specify a path to a specific playbook to debug with all vars')
@click.option('--cleanup', is_flag=True,
              help='Deletes environment')
@click.help_option('--help', '-h')
@click.option('-v', '--verbose', count=True)

def launch_demo_env(num_nodes,
                    num_infra,
                    hexboard_size=None,
                    region=None,
                    ami=None,
                    no_confirm=False,
                    master_instance_type=None,
                    node_instance_type=None,
                    infra_instance_type=None,
                    keypair=None,
                    r53_zone=None,
                    cluster_id=None,
                    app_dns_prefix=None,
                    deployment_type=None,
                    console_port=443,
                    api_port=443,
                    package_version=None,
                    rhsm_user=None,
                    rhsm_pass=None,
                    skip_subscription_management=False,
                    use_certificate_repos=False,
                    aos_repo=None,
                    prerelease=False,
                    kerberos_user=None,
                    kerberos_token=None,
                    registry_url=None,
                    run_smoke_tests=False,
                    num_smoke_test_users=None,
                    run_only_smoke_tests=False,
                    default_password=None,
                    debug_playbook=None,
                    cleanup=False,
                    verbose=0):

  # Force num_masters = 3 because of an issue with API startup and ELB health checks and more
  num_masters = 3

  # If not running cleanup need to prompt for the R53 zone:
  if r53_zone is None:
    r53_zone = click.prompt('R53 zone')

  # Cannot run cleanup with no-confirm
  if cleanup and no_confirm:
    click.echo('Cannot use --cleanup and --no-confirm as it is not safe.')
    sys.exit(1)

  # If skipping subscription management, must have cert repos enabled
  # If cleaning up, this is ok
  if not cleanup:
    if skip_subscription_management and not use_certificate_repos:
      click.echo('Cannot skip subscription management without using certificate repos.')
      sys.exit(1)

  # If using subscription management, cannot use certificate repos
  if not skip_subscription_management and use_certificate_repos:
    click.echo('Must skip subscription management when using certificate repos')
    sys.exit(1)

  # Prompt for RHSM user and password if not skipping subscription management
  if not skip_subscription_management:
    # If the user already provided values, don't bother asking again
    if rhsm_user is None:
      rhsm_user = click.prompt("RHSM username?")
    if rhsm_pass is None:
      rhsm_pass = click.prompt("RHSM password?", hide_input=True, confirmation_prompt=True)

  # User must supply a repo URL if using certificate repos
  if use_certificate_repos and aos_repo is None:
    click.echo('Must provide a repo URL via --aos-repo when using certificate repos')
    sys.exit(1)

  # User must supply kerberos user and token with --prerelease
  if prerelease and ( kerberos_user is None or kerberos_token is None ):
    click.echo('Must provider --kerberos-user / --kerberos-token with --prerelease')
    sys.exit(1)

  # Override hexboard size calculation
  if hexboard_size is None:
    if num_nodes <= 1:
      hexboard_size = 'tiny'
    elif num_nodes < 3:
      hexboard_size = 'xsmall'
    elif num_nodes < 5:
      hexboard_size = 'small'
    elif num_nodes < 9:
      hexboard_size = 'medium'
    elif num_nodes < 15:
      hexboard_size = 'large'
    else:
      hexboard_size = 'xlarge'

  # Calculate various DNS values
  host_zone="%s.%s" % (cluster_id, r53_zone)
  wildcard_zone="%s.%s.%s" % (app_dns_prefix, cluster_id, r53_zone)

  # Display information to the user about their choices
  click.echo('Configured values:')
  click.echo('\tcluster_id: %s' % cluster_id)
  click.echo('\tami: %s' % ami)
  click.echo('\tregion: %s' % region)
  click.echo('\tmaster instance_type: %s' % master_instance_type)
  click.echo('\tnode_instance_type: %s' % node_instance_type)
  click.echo('\tinfra_instance_type: %s' % infra_instance_type)
  click.echo('\tkeypair: %s' % keypair)
  click.echo('\tnodes: %s' % num_nodes)
  click.echo('\tinfra nodes: %s' % num_infra)
  click.echo('\tmasters: %s' % num_masters)
  click.echo('\tconsole port: %s' % console_port)
  click.echo('\tapi port: %s' % api_port)
  click.echo('\tdeployment_type: %s' % deployment_type)
  click.echo('\tpackage_version: %s' % package_version)

  if use_certificate_repos:
    click.echo('\taos_repo: %s' % aos_repo)

  click.echo('\tprerelease: %s' % prerelease)

  if prerelease:
    click.echo('\tkerberos user: %s' % kerberos_user)
    click.echo('\tkerberos token: %s' % kerberos_token)

  click.echo('\tregistry_url: %s' % registry_url)
  click.echo('\thexboard_size: %s' % hexboard_size)
  click.echo('\tr53_zone: %s' % r53_zone)
  click.echo('\tapp_dns_prefix: %s' % app_dns_prefix)
  click.echo('\thost dns: %s' % host_zone)
  click.echo('\tapps dns: %s' % wildcard_zone)

  # Don't bother to display subscription manager values if we're skipping subscription management
  if not skip_subscription_management:
    click.echo('\trhsm_user: %s' % rhsm_user)
    click.echo('\trhsm_pass: *******')

  if run_smoke_tests or run_only_smoke_tests:
    click.echo('\tnum smoke users: %s' % num_smoke_test_users)

  click.echo('\tdefault password: %s' % default_password)

  click.echo("")

  if run_only_smoke_tests:
    click.echo('Only smoke tests will be run.')

  if debug_playbook:
    click.echo('We will debug the following playbook: %s' % (debug_playbook))

  if not no_confirm and not cleanup:
    click.confirm('Continue using these values?', abort=True)

  # Special confirmations for cleanup
  if cleanup:
    click.confirm('Delete the cluster %s' % cluster_id, abort=True)
    click.confirm('ARE YOU REALLY SURE YOU WANT TO DELETE THE CLUSTER %s' % cluster_id, abort=True)
    click.confirm('Press enter to continue', abort=True, default=True)

  playbooks = []

  if debug_playbook:
    playbooks = [debug_playbook]
  elif run_only_smoke_tests:
    playbooks = ['playbooks/projects_setup.yml']
  elif cleanup:
    playbooks = ['playbooks/cleanup.yml']
  else:

    # start with the basic setup
    playbooks = ['playbooks/cloudformation_setup.yml']

    # if cert repos, then add that playbook
    if use_certificate_repos:
      playbooks.append('playbooks/certificate_repos.yml')

    # if not cert repos, add the register hosts playbook
    if not use_certificate_repos:
      playbooks.append('playbooks/register_hosts.yml')
    
    # add the setup and projects playbooks
    playbooks.append('playbooks/openshift_setup.yml')
    playbooks.append('playbooks/projects_setup.yml')

  for playbook in playbooks:

    # hide cache output unless in verbose mode
    devnull='> /dev/null'

    if verbose > 0:
      devnull=''

    # refresh the inventory cache to prevent stale hosts from
    # interferring with re-running
    command='inventory/aws/hosts/ec2.py --refresh-cache %s' % (devnull)
    os.system(command)

    # remove any cached facts to prevent stale data during a re-run
    command='rm -rf .ansible/cached_facts'
    os.system(command)

    command='ansible-playbook -i inventory/aws/hosts -e \'cluster_id=%s \
    ec2_region=%s \
    ec2_image=%s \
    ec2_keypair=%s \
    ec2_master_instance_type=%s \
    ec2_infra_instance_type=%s \
    ec2_node_instance_type=%s \
    r53_zone=%s \
    r53_host_zone=%s \
    r53_wildcard_zone=%s \
    console_port=%s \
    api_port=%s \
    num_app_nodes=%s \
    num_infra_nodes=%s \
    num_masters=%s \
    hexboard_size=%s \
    deployment_type=%s \
    package_version=-%s \
    rhsm_user=%s \
    rhsm_pass=%s \
    skip_subscription_management=%s \
    use_certificate_repos=%s \
    aos_repo=%s \
    prerelease=%s \
    kerberos_user=%s \
    kerberos_token=%s \
    registry_url=%s \
    run_smoke_tests=%s \
    run_only_smoke_tests=%s \
    num_smoke_test_users=%s \
    default_password=%s\' %s' % (cluster_id,
                    region,
                    ami,
                    keypair,
                    master_instance_type,
                    infra_instance_type,
                    node_instance_type,
                    r53_zone,
                    host_zone,
                    wildcard_zone,
                    console_port,
                    api_port,
                    num_nodes,
                    num_infra,
                    num_masters,
                    hexboard_size,
                    deployment_type,
                    package_version,
                    rhsm_user,
                    rhsm_pass,
                    skip_subscription_management,
                    use_certificate_repos,
                    aos_repo,
                    prerelease,
                    kerberos_user,
                    kerberos_token,
                    registry_url,
                    run_smoke_tests,
                    run_only_smoke_tests,
                    num_smoke_test_users,
                    default_password,
                    playbook)

    if verbose > 0:
      command += " -" + "".join(['v']*verbose)
      click.echo('We are running: %s' % command)

    status = os.system(command)
    if os.WIFEXITED(status) and os.WEXITSTATUS(status) != 0:
      return os.WEXITSTATUS(status)

  # if the last run playbook didn't explode, assume cluster provisioned successfully
  # but make sure that user was not just running tests or cleaning up
  if os.WIFEXITED(status) and os.WEXITSTATUS(status) == 0:
    if not debug_playbook and not run_only_smoke_tests and not cleanup:
      click.echo('Your cluster provisioned successfully. The console is available at https://openshift.%s:%s' % (host_zone, console_port))
      click.echo('You can SSH into a master using the same SSH key with: ssh -i /path/to/key.pem openshift@openshift-master.%s' % (host_zone))
      click.echo('**After logging into the OpenShift console** you will need to visit https://metrics.%s and accept the Hawkular SSL certificate' % ( wildcard_zone ))
      click.echo('You can access Kibana at https://kibana.%s' % ( wildcard_zone ))

    if cleanup:
      click.echo('Your cluster, %s, was de-provisioned and removed successfully.' % (cluster_id))

if __name__ == '__main__':
  # check for AWS access info
  if os.getenv('AWS_ACCESS_KEY_ID') is None or os.getenv('AWS_SECRET_ACCESS_KEY') is None:
    print 'AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY **MUST** be exported as environment variables.'
    sys.exit(1)

  launch_demo_env(auto_envvar_prefix='OSE_DEMO')

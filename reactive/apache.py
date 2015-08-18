import os
import yaml
from subprocess import check_call

from charmhelpers import fetch
from charmhelpers.core import host
from charmhelpers.core import hookenv
from charmhelpers.core import templating

from charms import reactive
from charms.reactive import hook
from charms.reactive import when
from charms.reactive import when_not


@hook('install')
def install():
    if reactive.is_state('apache.available'):
        return
    with open('apache.yaml') as fp:
        workload = yaml.safe_load(fp)
    install_packages(workload)
    for name, site in workload['sites'].items():
        install_site(name, site)
    hookenv.status_set('maintenance', '')
    reactive.set_state('apache.available')


def install_packages(workload):
    config = hookenv.config()
    hookenv.status_set('maintenance', 'Installing packages')
    packages = ['apache2', 'php5-cgi', 'libapache2-mod-php5']
    packages.extend(workload['packages'])
    fetch.apt_install(fetch.filter_installed_packages(packages))
    host.service_stop('apache2')
    check_call(['a2dissite', '000-default'])
    hookenv.open_port(config['port'])


def install_site(name, site):
    config = hookenv.config()
    hookenv.status_set('maintenance', 'Downloading %s' % name)
    dest = '/var/www/%s' % name
    fetch.install_remote(dest=dest, **site['install_from'])
    strip_archive_dir(dest)
    hookenv.status_set('maintenance', 'Installing %s' % name)
    templating.render(
        source='site',
        target='/etc/apache2/sites-available/%s' % name,
        context={
            'name': name,
            'site': site,
            'port': config['port'],
            'doc_root': dest,
        },
    )


def strip_archive_dir(site_dir):
    """
    Most archives will nest all contents under a single path, for ease of
    unpacking.  However, we want the site contents to reside directly within
    the site dir, which should be named based on the site entry.  This
    heuristic detects when an archive extracted to a single top-level
    dir within the site dir and moves the contents up.
    """
    contents = os.listdir(site_dir)
    if len(contents) == 1 and os.path.isdir(contents[0]):
        tmp_src = os.path.join(site_dir, contents[0])
        tmp_dest = os.path.join(os.path.dirname(site_dir), contents[0])
        os.rename(tmp_src, tmp_dest)
        os.rmdir(site_dir)
        os.rename(tmp_dest, site_dir)


@when('apache.start')
@when_not('apache.started')
def start_apache():
    workload = yaml.load('apache.yaml')
    for name, site in workload['sites'].items():
        check_call(['a2ensite', name])
    host.service_start('apache2')
    reactive.set_state('apache.started')


@when('apache.available', 'apache.started')
@when_not('apache.start')
def stop_apache():
    host.service_stop('apache2')
    reactive.remove_state('apache.started')


@when('website.available')
def configure_website(website):
    config = hookenv.config()
    website.configure(config['port'])

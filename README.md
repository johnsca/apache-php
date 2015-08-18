# Overview

This is a runtime layer that is intended to be built upon by other charm layers.
It provides Apache2 and modphp5, and manages sites based on an `apache.yaml`
defined in the charm layer that uses this.


# Usage

In your charm layer's `composer.yaml`, you will need to include this layer, e.g.:

    includes: ['layers:apache-php']

Then, you will need to include an `apache.yaml` file which can specify additional
packages to install, and one or more sites to install and manage.  Each site
definition should include an `install_from` section whose keys are arguments to
[install_remote][] and should at a minimum include a `source` value.  It can also
include an `options` value, to be used for the [Options directive][], and a
`server_name` value, to be used for the [ServerName directive][] and which can
reference config options via `{config["<key>"]}` interpolation.  An example
`apache.yaml` might look like:

    packages:
        - 'php5-mysql'
        - 'php5-gd'
    sites:
        vanilla:
            server_name: '{config["hostname"]}'
            options: 'Indexes FollowSymLinks MultiViews'
            install_from:
                source: https://github.com/vanillaforums/Garden/archive/Vanilla_2.0.18.8.tar.gz
                checksum: acf61a7ffca9359c1e1d721777182e51637be59744925935291801ccc8e8fd55
                hash_type: sha256

Your site will be installed in to `/var/www/<site>` where `<site>` is the name
of your site entry (`vanilla` in the example above).

Finally, your charm layer will need to interact with this layer via [reactive][]
states.  This layer will set the `apache.available` state once your `apache.yaml`
has been processed and all sites installed, at which point your charm layer
should perform any additional setup (such as creating site config files, opening
the appropriate ports, etc) and then set the `apache.start` state.


[install_remote]: http://pythonhosted.org/charmhelpers/api/charmhelpers.fetch.html#charmhelpers.fetch.install_remote
[reactive]: http://pythonhosted.org/charms.reactive/
[Options directive]: http://httpd.apache.org/docs/2.2/mod/core.html#options
[ServerName directive]: http://httpd.apache.org/docs/2.2/mod/core.html#servername

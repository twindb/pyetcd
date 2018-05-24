=======================================
Using Vagrant for tests and development
=======================================

There are four vagrant machines that are used for development and testing.

- **infra0, infra1** - Two machines that form the initial two nodes etcd cluster.
    ``make start`` will provision and start the etcd cluster.
- **infra2** - the additional node that can be used to extend the cluster to three nodes.
- **client** - is an empty machine configured with a base profile.
    It is supposed to work as a client for the etcd cluster.


To provision the vagrant machines run ``make start``. It will provision a two nodes etcd cluster
on ``infra0`` and ``infra1``. It will also start ``infra2``, but will not provision it.

As the Makefile targets may change in future run ``make`` to see currently implemented list of targets.

class profile::etcdnode {
    include profile::base

    package { ['etcd']:
        ensure => latest
    }

    service { 'etcd':
        ensure => running,
        require => Package['etcd']
    }
}

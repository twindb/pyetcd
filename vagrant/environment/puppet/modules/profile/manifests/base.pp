class profile::base {
  $user = 'vagrant'
  user { $user:
    ensure => present
  }

  file { "/home/${user}":
    ensure => directory,
    owner  => $user,
    mode   => "0750"
  }

  file { "/home/${profile::base::user}/.bashrc":
    ensure => present,
    owner  => $profile::base::user,
    mode   => "0644",
    source => 'puppet:///modules/profile/bashrc',
  }

  file { '/root/.ssh':
    ensure => directory,
    owner => 'root',
    mode => '700'
  }

  file { '/root/.ssh/authorized_keys':
    ensure => present,
    owner => 'root',
    mode => '600',
    source => 'puppet:///modules/profile/id_rsa.pub'
  }

  file { '/root/.ssh/id_rsa':
    ensure => present,
    owner => 'root',
    mode => '600',
    source => 'puppet:///modules/profile/id_rsa'
  }

    package { 'epel-release':
        ensure   => installed,
    }

    $packages = [ 'vim-enhanced', 'python2-pip', 'jq']

    package { $packages:
        ensure => installed,
        require => [Package['epel-release']]
    }

    package { ['tox']:
        ensure => installed,
        provider => pip,
        require => Package['python2-pip']
    }

}

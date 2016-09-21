=====
Usage
=====

Connect to local etcd instance. Write a key and read it after::

    from pyetcd.client import Client

    client = Client()
    client.write('/message', 'Hello world')
    response = client.read('/message')

    print(response.node['value'])


Write and read from a remote etcd cluster::

    from pyetcd.client import Client

    client = Client([
        '10.0.1.10',
        '10.0.1.11',
        '10.0.1.12'
    ])
    client.write('/message', 'Hello world')
    response = client.read('/message')

    print(response.node['value'])

Watch a key::

    from pyetcd.client import Client

    client = Client([
        '10.0.1.10',
        '10.0.1.11',
        '10.0.1.12'
    ])
    client.write('/message', 'Hello world')
    response = client.read('/message', wait=True)

    print(response.node['value'])

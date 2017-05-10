orloclient
==========

Python client for the [Orlo](https://github.com/eBayClassifiedsGroup/orlo) server.

Installation
------------

::

    pip install orloclient

Configuration
-------------

If orlo server is on the same box, put a section in /etc/orlo.ini:

::

    [client]
    uri=http://orlo.host

Otherwise, orloclient will read the ini file above from ``~/.orlo.ini`` or ``
./orlo.ini``.

This is the only configuration at present and is not required, it just saves you from
constantly having to type ``--uri http://orlo.host`` on the command line.

Command-line Usage
------------------

With an Orlo server running on localhost:5000, and client/uri configured in orlo.ini:

::

    $ orloclient create-release -p test -u alex
    Created release with id e42a478f-cc08-42e9-a9fb-c98ec65c414d

    $ orloclient create-package e42a478f-cc08-42e9-a9fb-c98ec65c414d test-package 1.0.0
    Created package with id 7510ffc0-4f0e-4fc1-925f-96ecb84e6db8

    $ orloclient start 7510ffc0-4f0e-4fc1-925f-96ecb84e6db8

    $ orloclient stop 7510ffc0-4f0e-4fc1-925f-96ecb84e6db8

    $ orloclient list
    [
      {
        "user": "alex",
        "platforms": [
          "test"
        ],
        "packages": [
          {
            "status": "SUCCESSFUL",
            "release_id": "e42a478f-cc08-42e9-a9fb-c98ec65c414d",
            "id": "7510ffc0-4f0e-4fc1-925f-96ecb84e6db8",
            {...}
          }
        ],
        {..}
      }
    ]


See ``orloclient -h`` for more details.


Usage in Python
---------------

::

    vagrant@debian-jessie:/vagrant$ ipython
    Python 2.7.9 (default, Mar  1 2015, 12:57:24)
    Type "copyright", "credits" or "license" for more information.

    IPython 4.0.1 -- An enhanced Interactive Python.
    ?         -> Introduction and overview of IPython's features.
    %quickref -> Quick reference.
    help      -> Python's own help system.
    object?   -> Details about 'object', use 'object??' for extra details.

    In [1]: import orloclient, json

    In [2]: client = orloclient.OrloClient(uri='http://localhost:5000')

    In [3]: release = client.create_release(user='alex', platforms=['alexdev'])

    In [4]: package = client.create_package(release, name='package-one', version='1.0.0')

    In [5]: client.package_start(package)
    Out[5]: True

    In [6]: client.package_stop(package)
    Out[6]: True

    In [7]: client.release_stop(release)
    Out[7]: True

    In [8]: doc = client.get_release_json(release.id)

    In [9]: print(json.dumps(doc, indent=2))
    {
      "releases": [
        {
          "platforms": [
            "alexdev"
          ],
          "ftime": "2016-03-03T16:56:03Z",
          "stime": "2016-03-03T16:55:05Z",
          "team": null,
          "duration": 57,
          "references": [],
          "packages": [
            {
              "status": "SUCCESSFUL",
              "rollback": false,
              "name": "package-one",
              "version": "1.0.0",
              "ftime": "2016-03-03T16:55:56Z",
              "stime": "2016-03-03T16:55:52Z",
              "duration": 4,
              "diff_url": null,
              "id": "9877cd69-1196-42dc-8d6c-0b7c95e11a5d"
            }
          ],
          "id": "700ff271-f705-4bfb-8582-b74633759feb",
          "user": "alex"
        }
      ]
    }


Tests
-----

There are two test suites, test_orloclient and test_integration. The former tests the orlo client functions while mocking the requests library, courtesy of HTTPretty <https://github.com/gabrielfalcao/HTTPretty>, while the integration tests run an actual Orlo server to test against.

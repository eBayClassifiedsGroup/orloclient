# orloclient

Python client for the [Orlo](https://github.com/eBayClassifiedsGroup/orlo) server.

# Installation
```
pip install orloclient
```

# Usage

With an Orlo server running on localhost:5000:
```python
$ python
Python 2.7.10 (default, Jul 13 2015, 12:05:58)
[GCC 4.2.1 Compatible Apple LLVM 6.1.0 (clang-602.0.53)] on darwin
Type "help", "copyright", "credits" or "license" for more information.
>>> from orloclient import Orlo
>>> orlo = Orlo(
...     uri='http://localhost:5000'
... )
>>> release_id = orlo.create_release(
...     user='testuser',
...     platforms=['dc1', 'dc2'],
...     team='A-Team',
...     references=['test-ticket1']
... )
>>> first_package_id = orlo.create_package(
...     release_id=release_id,
...     name='first_package',
...     version='1.0.0',
... )
>>> second_package_id = orlo.create_package(
...     release_id=release_id,
...     name='second_package',
...     version='2.0.0',
... )
>>> orlo.package_start(release_id=release_id, package_id=first_package_id)
True
>>> orlo.package_stop(release_id=release_id, package_id=first_package_id, success=True)
True
>>> orlo.package_start(release_id=release_id, package_id=second_package_id)
True
>>> orlo.package_stop(release_id=release_id, package_id=second_package_id, success=False)
True
>>> orlo.release_stop(release_id)
True
>>> orlo.get_releases(release_id=release_id)
>>> import json
>>> release = orlo.get_releases(release_id)
>>> print(json.dumps(release, indent=4, sort_keys=True))
{
    "releases": [
        {
            "duration": 224,
            "ftime": "2015-11-24T19:23:24Z",
            "id": "3155d4ce-b7c2-4d36-88ed-1d12d70fee8b",
            "packages": [
                {
                    "diff_url": null,
                    "duration": 64,
                    "ftime": "2015-11-24T19:22:13Z",
                    "id": "db0c8cc2-d87a-45ca-b8c1-48a3d7296e0a",
                    "name": "second_package",
                    "status": "FAILED",
                    "stime": "2015-11-24T19:21:08Z",
                    "version": "2.0.0"
                },
                {
                    "diff_url": null,
                    "duration": 19,
                    "ftime": "2015-11-24T19:22:04Z",
                    "id": "e3f758a1-4f87-4638-9186-2860eab88385",
                    "name": "first_package",
                    "status": "SUCCESSFUL",
                    "stime": "2015-11-24T19:21:45Z",
                    "version": "1.0.0"
                }
            ],
            "platforms": [
                "dc1",
                "dc2"
            ],
            "references": [
                "test-ticket1"
            ],
            "stime": "2015-11-24T19:19:40Z",
            "team": "A-Team",
            "user": "testuser"
        }
    ]
}
```

# Tests

There are two test suites, test_orloclient and test_integration. The former tests the orlo client functions while mocking the requests library, courtesy of [HTTPretty](https://github.com/gabrielfalcao/HTTPretty), while the integration tests run an actual Orlo server to test against.

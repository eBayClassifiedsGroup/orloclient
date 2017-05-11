from __future__ import print_function
import argparse
import logging
import json
import sys
import uuid
from os.path import expanduser
from orloclient import __version__
from orloclient import OrloClient

if sys.version_info >= (3, 0):
    from configparser import ConfigParser
else:
    from ConfigParser import ConfigParser


__author__ = 'alforbes'

logging.basicConfig(format='%(message)s')
logger = logging.getLogger('orloclient')
logger.setLevel(logging.INFO)


config = ConfigParser()
config.add_section('client')
config.set('client', 'uri', 'http://localhost:5000')
config.set('client', 'verify_ssl', 'true')
config.read([
    '/etc/orlo/orlo.ini',
    expanduser('~/.orlo.ini'),
    'orlo.ini',
])


def action_get_release(client, args):
    release = client.get_release(args.release)
    logger.info(json.dumps(
        release.data,
        indent=2
    ))


def action_get_package(client, args):
    package = client.get_package(args.package)
    logger.info(json.dumps(
        package.data,
        indent=2
    ))


def action_create_release(client, args):
    release = client.create_release(
        user=args.user,
        platforms=args.platforms,
        team=args.team,
        references=args.references,
        note=args.note,
    )
    logger.debug(release)
    logger.info('Created release with id {}'.format(release.id))
    return release


def action_create_package(client, args):
    release = client.get_release(args.release)
    package = client.create_package(
        release, args.name, args.version
    )
    logger.debug(package)
    logger.info('Created package with id {}'.format(package.id))
    return package


def action_start(client, args):
    package = client.get_package(args.package)
    release = client.get_release(package.release_id)

    client.package_start(package)
    release.fetch()

    logger.info(json.dumps(
        [
            p.to_dict() for p in release.packages \
                if p.id == uuid.UUID(package.id)
        ][0]
    ))


def action_stop(client, args):
    package = client.get_package(args.package)
    release = client.get_release(package.release_id)

    client.package_stop(package)
    release.fetch()

    logger.info(json.dumps(
        [
            p.to_dict() for p in release.packages \
            if p.id == uuid.UUID(package.id)
            ][0]
    ))


def action_list(client, args):
    logger.debug('Filters: {}'.format(str(args.filter)))
    kwargs = {}

    for filter in args.filter:
        l = filter.split('=')
        if len(l) != 2:
            logger.error("Invalid filter {}".format(str(filter)))
            raise SystemExit(2)
        kwargs[l[0]] = l[1]


    if args.packages:
        out = client.get_packages(raw=True, **kwargs)
    else:
        out = client.get_releases(raw=True, **kwargs)

    if args.id_only:
        print(json.dumps([item['id'] for item in out], indent=2))
    else:
        print(json.dumps(out, indent=2))


def action_stats(client, args):
    out = client.get_stats(
        field=args.field,
        name=args.name,
        platform=args.platform,
        stime=args.time_after,
        ftime=args.time_before,
    )
    print(json.dumps(out, indent=2))


def action_info(client, args):
    out = client.get_info(
        field=args.field,
        name=args.name,
        platform=args.platform,
    )
    print(json.dumps(out, indent=2))


def action_versions(client, args):
    out = client.get_versions(platform=args.platform)
    print(json.dumps(out, indent=2))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--version', '-v', action='version',
                        version='%(prog)s {}'.format(__version__))
    parser.add_argument('--uri', '-u', dest='uri',
                        default=config.get('client', 'uri'),
                        help="Address of orlo server")
    parser.add_argument('--debug', '-d', help='Enable debug logging',
                        action='store_true')
    parser.add_argument(
        '--insecure', '-I', action='store_true',
        default=False if config.getboolean('client', 'verify_ssl') else True,
        help='Do not verify SSL/TLS connections')

    subparsers = parser.add_subparsers(dest='object')
    pp_package = argparse.ArgumentParser(add_help=False)
    pp_package.add_argument(
        'package', help='ID of the package to operate on',
    )

    pp_release = argparse.ArgumentParser(add_help=False)
    pp_release.add_argument(
        'release', help='ID of the release to operate on',
    )

    pp_create_release = argparse.ArgumentParser(add_help=False)
    pp_create_release.add_argument(
        '-p', '--platform', help='Platforms field value', nargs='+',
        dest='platforms', required=True,
    )
    pp_create_release.add_argument(
        '-u', '--user', help='Username field value', required=True,
    )
    pp_create_release.add_argument(
        '-t', '--team', help='Team field value', required=False
    )
    pp_create_release.add_argument(
        '-r', '--references', help='References field value', nargs='+',
    )
    pp_create_release.add_argument(
        '-n', '--note', help='Note field value',
    )

    pp_list = argparse.ArgumentParser(add_help=False)
    pp_list.add_argument(
        'filter', nargs='*',
        help="Filters in the form parameter=value. See "
             "http://orlo.readthedocs.io/en/latest/rest.html#get--releases "
             "for valid parameters"
    )
    pp_list.add_argument(
        '-p', '--packages', action='store_true',
        help="By default we list releases, this switches to listing "
             "packages instead"
    )
    pp_list.add_argument(
        '-i', '--id-only', action='store_true',
       help="Only print id values, not full release json"
    )

    pp_info = argparse.ArgumentParser(add_help=False)
    pp_info.add_argument('field', help='Field to report on',
                         choices=('users', 'teams', 'packages', 'platforms'))
    pp_info.add_argument('--name', help='The subject or field entry, e.g if '
                                        'field is user, name could be "alex"')
    pp_info.add_argument('--platform', help='Platform to filter on.')

    pp_stats = argparse.ArgumentParser(add_help=False)
    pp_stats.add_argument('--field', help='Field to report on',
                          choices=('user', 'team', 'package', 'platform'))
    pp_stats.add_argument('--name', help='The subject or field entry, e.g if '
                                         'field is user, name could be "alex"')
    pp_stats.add_argument('--platform', help='Platform to filter on.')
    pp_stats.add_argument('--time-before', metavar='TIME',
                          help='Filter by releases started before this time')
    pp_stats.add_argument('--time-after', metavar='TIME',
                          help='Filter by releases started after this time'
                          '(both time-before and time-after filter on the '
                          '"stime" [start time] field).')


    pp_versions = argparse.ArgumentParser(add_help=False)
    pp_versions.add_argument('--platform', help='Platform to filter on')

    pp_create_package = argparse.ArgumentParser(add_help=False)
    pp_create_package.add_argument('name', help='Package name')
    pp_create_package.add_argument('version', help='Package version')

    subparsers.add_parser(
        'create-release', help='Create a release',
        parents=[pp_create_release]
    ).set_defaults(func=action_create_release)
    subparsers.add_parser(
        'create-package', help='Create a package',
        parents=[pp_release, pp_create_package]
    ).set_defaults(func=action_create_package)
    subparsers.add_parser(
        'get-release', help='Fetch a release by ID',
        parents=[pp_release]
    ).set_defaults(func=action_get_release)
    subparsers.add_parser(
        'get-package', help='Fetch a package by id',
        parents=[pp_package]
    ).set_defaults(func=action_get_package)
    subparsers.add_parser(
        'start', help='Start a package',
        parents=[pp_package]
    ).set_defaults(func=action_start)
    subparsers.add_parser(
        'stop', help='Stop a package',
        parents=[pp_package]
    ).set_defaults(func=action_stop)
    subparsers.add_parser(
        'list', help='List releases, filters optional',
        parents=[pp_list]
    ).set_defaults(func=action_list)
    subparsers.add_parser(
        'stats', help='Fetch release stats',
        parents=[pp_stats]
    ).set_defaults(func=action_stats)
    subparsers.add_parser(
        'info', help='Fetch release info',
        parents=[pp_info]
    ).set_defaults(func=action_info)
    subparsers.add_parser(
        'versions', help='Fetch current package versions',
        parents=[pp_versions]
    ).set_defaults(func=action_versions)

    args = parser.parse_args()
    if args.debug:
        logger.setLevel(logging.DEBUG)
    logger.debug(args)

    client = OrloClient(
        uri=args.uri,
        verify_ssl=False if args.insecure else True,
    )
    args.func(client, args)


if __name__ == "__main__":
    main()

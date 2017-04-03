from __future__ import print_function
import argparse
import logging
import json
import uuid
from orloclient import __version__
from orloclient import OrloClient

__author__ = 'alforbes'

logging.basicConfig(format='%(message)s')
logger = logging.getLogger('orloclient')
logger.setLevel(logging.INFO)


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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--version', '-v', action='version',
                        version='%(prog)s {}'.format(__version__))
    parser.add_argument('--uri', '-u', dest='uri',
                        default='http://localhost:5000',
                        help="Address of orlo server")
    parser.add_argument('--debug', help='Enable debug logging',
                        action='store_true')

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

    pp_create_package = argparse.ArgumentParser(add_help=False)
    pp_create_package.add_argument('name', help='Package name')
    pp_create_package.add_argument('version', help='Package version')

    se = subparsers.add_parser(
        'create_release', help='Create a release',
        parents=[pp_create_release]
    ).set_defaults(func=action_create_release)
    subparsers.add_parser(
        'create_package', help='Create a package',
        parents=[pp_release, pp_create_package]
    ).set_defaults(func=action_create_package)
    subparsers.add_parser(
        'get_release', help='Fetch a release by ID',
        parents=[pp_release]
    ).set_defaults(func=action_get_release)
    subparsers.add_parser(
        'get_package', help='Fetch a package by id',
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

    args = parser.parse_args()
    if args.debug:
        logger.setLevel(logging.DEBUG)
    logger.debug(args)

    client = OrloClient(
        uri=args.uri
    )
    args.func(client, args)


if __name__ == "__main__":
    main()

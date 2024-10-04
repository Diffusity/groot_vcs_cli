import argparse
import os
import subprocess
import sys
import textwrap

from . import base
from . import data
from . import diff
from . import remote


def main():
    with data.change_git_dir('.'):
        args = parse_args()
        args.func(args)


def check_user():
    # Check if the user.txt file exists and has a username
    if not os.path.exists('user.txt'):
        print("Username not set. Please run the 'user' command first.")
        sys.exit(1)
    
    with open('user.txt', 'r') as f:
        username = f.read().strip()
        if not username:
            print("Username not set. Please run the 'user' command first.")
            sys.exit(1)


def parse_args():
    parser = argparse.ArgumentParser()

    commands = parser.add_subparsers(dest='command')
    commands.required = True

    oid = base.get_oid

    init_parser = commands.add_parser('init')
    init_parser.set_defaults(func=init)

    commit_parser = commands.add_parser('commit')
    commit_parser.set_defaults(func=commit)
    commit_parser.add_argument('-m', '--message', required=True)

    log_parser = commands.add_parser('log')
    log_parser.set_defaults(func=log)
    log_parser.add_argument('oid', default='@', type=oid, nargs='?')

    show_parser = commands.add_parser('show')
    show_parser.set_defaults(func=show)
    show_parser.add_argument('oid', default='@', type=oid, nargs='?')

    diff_parser = commands.add_parser('diff')
    diff_parser.set_defaults(func=_diff)
    diff_parser.add_argument('--cached', action='store_true')
    diff_parser.add_argument('commit', nargs='?')

    checkout_parser = commands.add_parser('checkout')
    checkout_parser.set_defaults(func=checkout)
    checkout_parser.add_argument('commit')

    branch_parser = commands.add_parser('branch')
    branch_parser.set_defaults(func=branch)
    branch_parser.add_argument('name', nargs='?')
    branch_parser.add_argument('start_point', default='@', type=oid, nargs='?')

    status_parser = commands.add_parser('status')
    status_parser.set_defaults(func=status)

    reset_parser = commands.add_parser('reset')
    reset_parser.set_defaults(func=reset)
    reset_parser.add_argument('commit', type=oid)

    push_parser = commands.add_parser('push')
    push_parser.set_defaults(func=push)
    push_parser.add_argument('branch')
    push_parser.add_argument('--name', required=True)

    add_parser = commands.add_parser('add')
    add_parser.set_defaults(func=add)
    add_parser.add_argument('files', nargs='+')
    
    user_parser = commands.add_parser('user')
    user_parser.set_defaults(func=user)

    return parser.parse_args()


def user(args):
    print("\n$ Note : This username you enter below will be used in the GROOT mobile application to fetch your directories from the databse...!\n")
    username = input("Enter your username: ").strip()
    if username:
        with open('user.txt', 'w') as f:
            f.write(username)
        print(f"\nUsername '{username}' set successfully.")
    else:
        print("Username cannot be empty.")


def init(args):
    check_user()
    base.init()
    print(f'Initialized empty groot repository in {os.getcwd()}/{data.GIT_DIR}')


def commit(args):
    check_user()
    print(base.commit(args.message))

def _print_commit(oid, commit, refs=None):
    refs_str = f' ({", ".join(refs)})' if refs else ''
    print(f'commit : {oid} : {refs_str}')
    print("Message: ", commit.message)
    print('')

def log(args):
    check_user()
    refs = {}
    for refname, ref in data.iter_refs():
        refs.setdefault(ref.value, []).append(refname)

    for oid in base.iter_commits_and_parents({args.oid}):
        commit = base.get_commit(oid)
        _print_commit(oid, commit, refs.get(oid))


def show(args):
    check_user()
    if not args.oid:
        return
    commit = base.get_commit(args.oid)
    parent_tree = None
    if commit.parents:
        parent_tree = base.get_commit(commit.parents[0]).tree

    _print_commit(args.oid, commit)
    result = diff.diff_trees(
        base.get_tree(parent_tree), base.get_tree(commit.tree))
    sys.stdout.flush()
    sys.stdout.buffer.write(result)


def _diff(args):
    check_user()
    oid = args.commit and base.get_oid(args.commit)

    if args.commit:
        tree_from = base.get_tree(oid and base.get_commit(oid).tree)

    if args.cached:
        tree_to = base.get_index_tree()
        if not args.commit:
            oid = base.get_oid('@')
            tree_from = base.get_tree(oid and base.get_commit(oid).tree)
    else:
        tree_to = base.get_working_tree()
        if not args.commit:
            tree_from = base.get_index_tree()

    result = diff.diff_trees(tree_from, tree_to)
    sys.stdout.flush()
    sys.stdout.buffer.write(result)


def checkout(args):
    check_user()
    base.checkout(args.commit)


def branch(args):
    check_user()
    if not args.name:
        current = base.get_branch_name()
        for branch in base.iter_branch_names():
            prefix = '*' if branch == current else ' '
            print(f'{prefix} {branch}')
    else:
        base.create_branch(args.name, args.start_point)
        print(f'Branch {args.name} created at {args.start_point[:10]}')


def status(args):
    check_user()
    HEAD = base.get_oid('@')
    branch = base.get_branch_name()
    if branch:
        print(f'On branch {branch}')
    else:
        print(f'HEAD detached at {HEAD[:10]}')

    MERGE_HEAD = data.get_ref('MERGE_HEAD').value
    if MERGE_HEAD:
        print(f'Merging with {MERGE_HEAD[:10]}')

    print('\nChanges to be committed:\n')
    HEAD_tree = HEAD and base.get_commit(HEAD).tree
    for path, action in diff.iter_changed_files(base.get_tree(HEAD_tree),
                                                base.get_index_tree()):
        print(f'{action:>12}: {path}')

    print('\nChanges not staged for commit:\n')
    for path, action in diff.iter_changed_files(base.get_index_tree(),
                                                base.get_working_tree()):
        print(f'{action:>12}: {path}')


def reset(args):
    check_user()
    base.reset(args.commit)


def push(args):
    check_user()
    with open('user.txt', 'r') as f:
        user = f.read()
        if args.name == user:
            remote.push(args.name, f'{args.branch}')
        else:
            print('Please enter proper username....!')


def add(args):
    check_user()
    base.add(args.files)


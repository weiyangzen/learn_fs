# sources/distributed-fs/tahoe-lafs/misc/build_helpers/test-git-ignore.py

## Purpose

This helper checks whether the current working tree is clean according to `git status --porcelain`.

## Important APIs, Types, and Functions

It uses `subprocess.Popen(["git", "status", "--porcelain"], stdout=PIPE)` and compares the captured output with an empty string.

## Control Flow

The script runs the command, prints raw output, exits `0` if it thinks the output is empty, otherwise exits `1`.

## State, Dependencies, Integration, Risks, and Tests

There is no persistent state. Dependency is Git in the current repository. Integration is build validation for generated or ignored files. The major risk is Python 3 behavior: `communicate()[0]` is bytes, so comparing to `""` is always false; in Python 3 this script reports dirty even for clean output. Tests should run under Python 2 and Python 3 or compare to `b""`, with clean, modified, and untracked fixtures.

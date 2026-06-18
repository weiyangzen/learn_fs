# sources/distributed-fs/tahoe-lafs/misc/checkers/check_grid.py

## Purpose

This operational checker exercises a pre-existing Tahoe grid through the CLI to verify that a new client can read old data, modify old and recent directories, upload new immutable data, and update mutable files.

## Important APIs, Types, and Functions

`GridTesterOptions` parses `--no`, a node directory, and a `tahoe` executable. `GridTester.command` wraps `subprocess.Popen` and return-code validation. `cli` prefixes commands with `tahoe -d NODEDIR`. Workflow helpers include `read_and_check`, `delete_and_check`, `listdir`, `put`, `put_mutable`, `update`, and `makefile`. `do_test` is the scenario driver.

## Control Flow

The script lists `testgrid:`, reads and checksum-validates `old.*` and `recent.*` files, deletes recent files, repeats similar checks in `recentdir`, recreates `recentdir`, uploads fresh random files named by MD5, appends timestamps to mutable logs, deletes `recentlog`, and recreates it as mutable.

## State, Dependencies, Integration, Risks, and Tests

State is remote Tahoe grid mutation plus local random data. Dependencies are Twisted `usage`, Python 2 `md5`, the Tahoe CLI, a running client node, and configured `testgrid` alias. Risks include destructive deletes, Python 2 string/bytes assumptions, no timeout around CLI commands, and md5 values embedded in filenames as the correctness oracle. Test signals are best provided by an isolated test grid fixture, with dry-run coverage for command construction and integration coverage for each CLI operation class.

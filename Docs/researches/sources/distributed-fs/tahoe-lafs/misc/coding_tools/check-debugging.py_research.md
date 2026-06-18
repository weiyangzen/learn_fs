# sources/distributed-fs/tahoe-lafs/misc/coding_tools/check-debugging.py

## Purpose

This Python 3 coding check rejects production use of `defer.setDebugging(True)` in Python source files.

## Important APIs, Types, and Functions

There are no functions. It walks each `sys.argv[1:]` starting directory with `os.walk`, filters `.py` files except itself, and applies regex `\.setDebugging\(True\)`.

## Control Flow

The first match prints a policy error and the file/line, then exits `1`. If the scan completes, it prints a success message and exits `0`.

## State, Dependencies, Integration, Risks, and Tests

State is only process exit status. Dependencies are stdlib `os`, `re`, and source paths. Integration is CI linting. Risks include matching comments or strings, missing alternate whitespace/call forms, and not pruning virtualenv/build directories unless caller scopes the scan. Tests should use fixture files with real calls, comments, strings, and varied whitespace.

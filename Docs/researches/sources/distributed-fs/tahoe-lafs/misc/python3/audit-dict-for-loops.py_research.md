# sources/distributed-fs/tahoe-lafs/misc/python3/audit-dict-for-loops.py

## Purpose

This Python 3 migration audit script runs `futurize`'s dict-loop fixer over all modules declared ported to Python 3, so developers can inspect diffs for unsafe mutation while iterating over dictionary views.

## Important APIs, Types, and Functions

`fix_potential_issue()` iterates `_python3.PORTED_MODULES + _python3.PORTED_TEST_MODULES`, maps module names to `src/...py` or package `__init__.py`, and runs `check_call(["futurize", "-f", "lib2to3.fixes.fix_dict", "-w", filename])`.

## Control Flow

When executed directly, it rewrites files in place and prints a reminder to inspect the diff. Missing `.py` module files are treated as packages.

## State, Dependencies, Integration, Risks, and Tests

Persistent state is modified source files. Dependencies are Tahoe `_python3` port lists and external `futurize`. Integration is manual Python 3 porting audits. Risks include broad in-place rewrites, typo in final message, failure if port lists include non-files, and no dry-run mode. Tests should monkeypatch `_python3` lists and `check_call`, and use a temporary fixture to verify module-to-path mapping.

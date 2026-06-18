# sources/distributed-fs/tahoe-lafs/src/allmydata/util/humanreadable.py

## Purpose

This module provides a richer `reprlib.Repr` implementation for logs and diagnostics. It gives better representations for functions, bound methods, exceptions, lists, and dictionaries, especially when objects are large or mutating concurrently.

## APIs and control flow

`BetterRepr` configures larger maxima than the stdlib defaults. `repr_function()` and `repr_instance_method()` include function names, basenames, and first line numbers. `repr_instance()` expands exception arguments with temporarily larger string/list limits and handles dict/list instances directly. `repr_list()` copies a slice to tolerate concurrent mutation; `repr_dict()` snapshots and sorts items. The module-level `brepr` instance backs `hr(x)`.

## State, dependencies, risks, and tests

State is the mutable global `brepr`, intentionally overridable by other code. Dependencies are `os.path.basename` and `reprlib.Repr`. Integration is logging/debug output throughout Tahoe.

Risks include sorting dict keys that are not mutually comparable, exposing file/line details in logs, and global mutable formatter settings affecting unrelated callers. Test signals should cover functions, builtins, bound methods, exceptions with one/many args, large lists/dicts/strings, concurrent-ish mutation snapshots, and overriding `brepr`.

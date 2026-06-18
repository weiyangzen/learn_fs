# Research: sources/security-integrity/selinux/python/sepolicy/sepolicy/communicate.py

## Purpose
This helper provides shared CLI-style behavior for communication/access analysis. It formats usage failures and computes allowed target types for a source domain, class, and permissions.

## Important APIs and control flow
`usage(parser, msg)` prints parser help, writes an error message to stderr, flushes, and exits with status 1. `expand_attribute(attribute)` calls `next(sepolicy.info(sepolicy.ATTRIBUTE, attribute))`, converts the returned `types` iterable to a list, and falls back to `[attribute]` on `StopIteration`. `get_types(src, tclass, perm)` searches allow rules, raises `ValueError` when none exist, filters rules whose `permlist` includes the requested permission set, expands target attributes, and returns the flat target list.

## State and persistence
There is no local mutable state and no direct persistence. The module may trigger lazy loading and caching inside `sepolicy`.

## Dependencies and integration points
Dependencies are `sys` and `sepolicy`. The module is intended for CLI entry points that have an argparse-like parser and need to compute communication targets from SELinux allow rules.

## Risks and edge cases
`usage()` calls `sys.exit()`, so it is hostile to library callers unless isolated. `get_types()` assumes `perm` is iterable and suitable for `set(perm)`. Passing a string permission accidentally creates a set of characters, not a one-permission set. Like `booleans.py`, the returned target list is not deduplicated and rule dictionaries without `permlist` will raise. Its no-allow exception type differs from `booleans.py`.

## Test signals
Tests should cover `usage()` output and exit, missing attributes, concrete targets, attribute expansion, no allow rules, string-versus-list permissions, and duplicate outputs. CLI tests should assert stderr flushing and exit code behavior.

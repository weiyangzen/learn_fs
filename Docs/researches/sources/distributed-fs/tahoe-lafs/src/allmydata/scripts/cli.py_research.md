# sources/distributed-fs/tahoe-lafs/src/allmydata/scripts/cli.py

## Purpose
Defines most user-facing Tahoe filesystem CLI option parsers and dispatch functions: aliases, `ls`, `get`, `put`, `cp`, `mv`, `ln`, `backup`, `webopen`, `manifest`, `stats`, `check`, `deep-check`, and `status`.

## APIs, Types, And Control Flow
The central base is `FileStoreOptions`, which resolves `--node-directory`, reads `node.url`, normalizes `--node-url`, loads aliases, and lets `--dir-cap` override the default alias. Command-specific subclasses parse and validate arguments and flags. `subCommands` exposes Twisted usage metadata, while `dispatch` maps command names to thin wrapper functions that import the implementation lazily and return its rc.

## State, Persistence, And Integration
Reads local node state from `node.url`, `private/root_dir.cap`, and `private/aliases`; most mutations happen in imported modules through the web API or alias files. It integrates with `common.get_aliases`, command modules such as `tahoe_put`, `tahoe_cp`, `tahoe_backup`, and `tahoe_check`, and the top-level `runner.dispatch`, which runs these blocking commands in a worker thread.

## Risks And Test Signals
Risks are mostly parsing and UX boundary cases: URL regex only accepts simple host/port HTTP(S) forms, `node.url` must exist unless explicitly overridden, Windows drive-letter paths interact with alias syntax in shared helpers, and command wrappers rely on lazy imports. Test signals are broad CLI tests under `allmydata/test/cli/`, including alias, list, put, cp, mv, backup, status, and check tests.

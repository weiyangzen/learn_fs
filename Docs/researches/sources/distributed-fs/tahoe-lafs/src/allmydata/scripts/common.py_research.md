# sources/distributed-fs/tahoe-lafs/src/allmydata/scripts/common.py

## Purpose
Contains shared CLI utilities for option formatting, basedir resolution, introducer and alias file handling, Tahoe alias/path parsing, platform drive-letter detection, and URL path escaping.

## APIs, Types, And Control Flow
`BaseOptions` customizes subcommand usage and forbids `--version` below the root command. `BasedirOptions` and `NoDefaultBasedirOptions` resolve `--basedir`, `--node-directory`, positional basedirs, and defaults with conflict checks. `write_introducer` writes `private/introducers.yaml`. `get_introducer_furl` reads configured introducers or falls back to `private/introducer.furl`. `get_aliases` reads root/default aliases and `private/aliases`. `get_alias` converts user paths into `(dircap, relative_path)` while accepting raw caps and handling default aliases. `escape_path` percent-encodes UTF-8 path segments.

## State, Persistence, And Integration
Writes `private/introducers.yaml`; reads `private/root_dir.cap`, `private/aliases`, and `private/introducer.furl`. It integrates with Twisted `usage`, YAML serialization, URI parsing, encoding utilities, and all CLI modules that need aliases or basedirs.

## Risks And Test Signals
Risks include ambiguous colon parsing, alias file lines split on the first colon, raw cap path suffix compatibility, and platform-specific Windows drive handling controlled by a test hook. `get_aliases` silently ignores file read errors, which is friendly but can hide permission problems. Test signals include CLI alias/path tests, create-node tests for introducer writing, and Windows path parsing tests.

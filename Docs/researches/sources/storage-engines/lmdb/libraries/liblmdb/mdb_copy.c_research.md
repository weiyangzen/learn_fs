# sources/storage-engines/lmdb/libraries/liblmdb/mdb_copy.c

## Purpose
`mdb_copy.c` implements the LMDB backup/copy command-line tool. It opens an existing environment read-only and copies it either to stdout or to a destination path, optionally using compact-copy mode and optional encrypted-environment hooks.

## Important APIs, types, and functions
The only local helper is an empty `sighandle` used to interrupt blocking writes cleanly. `main` parses `-n`, `-L`, `-v`, `-c`, `-V`, `-m`, and `-w`, creates an `MDB_env`, optionally loads crypto hooks with `mdb_modload`/`mdb_modsetup`, opens the environment with `mdb_env_open`, then calls `mdb_env_copyfd2` or `mdb_env_copy2`. It uses `MDB_CP_COMPACT`, `MDB_NOSUBDIR`, `MDB_NOLOCK`, `MDB_PREVSNAPSHOT`, and platform-specific stdout descriptors.

## Control flow
Argument parsing builds environment and copy flags before validating `srcpath [dstpath]`. Signal handlers are installed for pipe, hangup, interrupt, and terminate signals. The tool then creates the environment, attaches crypto if requested, opens the source read-only, copies to stdout when no destination is provided or to a filesystem destination otherwise, reports the failing action on error, and always closes the environment and unloads a module handle if present.

## State and persistence behavior
The source environment is read-only. The destination receives either a byte-for-byte or compacted LMDB copy. `MDB_PREVSNAPSHOT` allows copying a previous snapshot, while `MDB_NOLOCK` avoids lock-table coordination and shifts consistency responsibility to the caller.

## Dependencies and integration points
The file integrates with public LMDB environment copy APIs and with the local dynamic crypto module helper API. Build integration must link the platform dynamic-loader implementation when module support is used.

## Risks and edge cases
`-m` and `-w` consume the next argv entry without local bounds checks before the final argc validation, so malformed option ordering relies on later usage failure or may read a missing pointer. `MDB_NOLOCK` can produce unsafe copies if writers are active. Copying to stdout depends on SIGPIPE behavior and binary-safe descriptors. Crypto setup must match the source database or open/copy will fail.

## Test signals
Useful tests include copying normal and compact databases, stdout piping, NOSUBDIR environments, previous snapshots, encrypted databases with and without passwords, and interruption or broken-pipe exits.

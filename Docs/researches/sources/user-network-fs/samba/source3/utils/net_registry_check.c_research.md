# sources/user-network-fs/samba/source3/utils/net_registry_check.c

## Purpose
This file implements `net registry check`, a parser, validator, repairer, and rewriter for Samba registry TDB databases. It reconstructs a key tree from raw TDB records, detects malformed paths and tree metadata, and can repair in place or write a clean output database.

## Important APIs, Types, And Control Flow
The exported API is `net_registry_check_db()`. `struct regval` and `struct regkey` model decoded values, subkeys, security descriptors, and repair flags. `struct check_ctx` holds input/output db handles, in-memory key registry and deletion lists, database version, separator, options, and interaction defaults. Low-level readers parse uint32, C strings, blobs, and serialized registry values. `check_tdb_action()` classifies raw records as `INFO/version`, subkey lists, value lists, security descriptors, sorted subkeys, sequence records, or invalid keys. Paths are normalized for separator and uppercase form, with interactive/automatic skip/delete/edit/retry decisions. `read_subkeys()`, `read_values()`, and `read_sd()` populate the reconstructed tree. `get_version()` selects registry format version and path separator. Repair/write paths use `write_subkeylist()`, `write_sorted()`, `write_values()`, and `write_sd()`. Final actions either check tree warnings, repair in place, delete invalid keys, or wipe/write a new database.

## State And Persistence
Input opens read-only. Output opens when repair/output/write behavior is requested; automatic mode without output repairs the input file. Output writes are transactional and cancelled in test mode. In-memory dbwrap_rbt databases store the reconstructed key tree and invalid raw keys pending deletion.

## Dependencies And Integration Points
It depends on dbwrap/TDB, dbwrap_rbt, registry DB constants and prefixes, security descriptor marshal/unmarshal, registry parser internals, interactive prompting/editing, string parsing helpers, cbuf serialization, and `struct check_options` from `net_registry_check.h`. It is called from `net_registry.c`.

## Risks And Test Signals
Path normalization notes that it is not generally correct for multibyte characters. Some repairs are best-effort and several comments mark incomplete interaction behavior. Automatic mode can delete invalid records or rewrite the same database. `talloc_array_append()` frees the old array on realloc failure, which can lose existing state. Test version 1/2/3 separators, missing/invalid `INFO/version`, malformed non-NUL keys, duplicate subkey lists, mismatched subkey counts, trailing value data, missing parent references, invalid sorted subkeys, security descriptor decode failures, output `--wipe`, in-place repair, `--test`, `--lock`, `--auto`, `--force`, and explicit `--reg-version`.

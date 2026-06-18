# sources/sync-backup/borg/src/borg/archiver/debug_cmd.py

## Purpose

`debug_cmd.py` implements the `borg debug` command group. These commands expose low-level repository, manifest, archive, object, key, and profiling internals for diagnostics and recovery work, and are explicitly not intended for normal use. The source was read as a complete 530-line file.

## Important APIs, Types, and Functions

`DebugMixIn` provides `do_debug_info()`, `do_debug_dump_archive_items()`, `do_debug_dump_archive()`, `do_debug_dump_manifest()`, `do_debug_dump_repo_objs()`, `do_debug_search_repo_objs()`, `do_debug_get_obj()`, `do_debug_id_hash()`, `do_debug_parse_obj()`, `do_debug_format_obj()`, `do_debug_put_obj()`, `do_debug_delete_obj()`, and `do_debug_convert_profile()`. `build_parser_debug()` constructs the nested `debug` subcommands and arguments. Important helpers include `RepoObj.parse()/format()`, `key_factory()`, `msgpack` unpackers, `prepare_dump_dict()`, `StableDict`, `hex_to_bin()`, `bin_to_hex()`, and `dash_open()`.

## Control Flow

The debug commands use different repository wrappers depending on risk and required state. Metadata dump commands open a manifest with no operation compatibility check, load archive or manifest objects, parse encrypted/compressed repository objects through `manifest.repo_objs`, and stream JSON or binary files. Repository-object dump/search commands open the repository without a manifest, bootstrap a key from the first listed object, and iterate `repo_lister()`. Object get/put/delete commands convert user-supplied hex IDs to 32-byte IDs, then directly call repository get/put/delete. Parse/format object commands convert between raw object files plus JSON metadata and Borg object bytes. The parser nests all of these under `borg debug`.

## State and Persistence Behavior

Many commands write files in the current working directory or to user-supplied paths. `put-obj` directly inserts arbitrary bytes at a repository object ID, and `delete-obj` deletes repository objects under an exclusive lock. `format-obj` produces object files but does not store them unless combined with `put-obj`. Dump/search/info/id-hash commands are read-only with respect to the repository. Because some commands open without normal manifest checks, they can operate on partially corrupted repositories but also bypass guardrails.

## Dependencies and Integration Points

This module integrates with archive metadata layout (`ROBJ_ARCHIVE_META`, `ROBJ_ARCHIVE_CHUNKIDS`, `ROBJ_ARCHIVE_STREAM`), manifest object layout, repository object encryption/compression through `RepoObj`, key creation from repository content, and platform process info. It is a diagnostic backdoor into the same objects manipulated by create, extract, compact, and check.

## Risks and Edge Cases

The command group can corrupt repositories if used incorrectly, especially `put-obj`, `delete-obj`, and `format-obj`. Dumping archive metadata can create many files and large JSON outputs. `do_debug_dump_repo_objs()` assumes at least one repository object exists to bootstrap the key. Search only supports `hex:` and `str:` prefixes and keeps boundary data to find cross-object matches. Hex ID validation prevents wrong-length IDs but cannot ensure semantic object type correctness when formatting/inserting. Some commands intentionally suppress normal operation compatibility checks.

## Test Signals

Tests should use disposable repositories to verify manifest/archive dumps are parseable JSON, archive item dumps match item pointer streams, object get/parse/format round-trips preserve metadata and payload, invalid IDs raise `CommandError`, search finds in-object and cross-boundary byte sequences, empty/corrupt repository bootstrap failures are understandable, delete handles missing objects, and parser coverage confirms every debug subcommand is registered with expected arguments.

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/helpers.py -->
# sources/sync-backup/bup/lib/bup/helpers.py

## Purpose
This is the general-purpose support module for bup. It provides exit constants, process cleanup, atomic file replacement, fsync portability, mmap wrappers, protocol connection primitives, stream utilities, quoting, path reduction/grafting, exclusion parsing, error aggregation, and small formatting/parsing helpers.

## Important APIs, Types, And Functions
Important surfaces include `EXIT_*`, `notimplemented`, `finalized`, `temp_dir`, `stopped`, `fsync`/`fdatasync`, `merge_iter`, `atomically_replaced_file`, `BaseConn`, `Conn`, `DemuxConn`, `mux`, `chunkyreader`, `linereader`, `mmap_read*`, `parse_timestamp`, `parse_num`, `add_error`, `die_if_errors`, `parse_excludes`, `parse_rx_excludes`, `path_components`, `stripped_path_components`, `grafted_path_components`, `valid_save_name`, `period_as_secs`, and `make_repo_id`. `ObjectLocation`/`OBJECT_EXISTS` are used by storage lookups.

## Control Flow
Context managers dominate lifecycle: `stopped` terminates child processes on exit, `finalized` wraps arbitrary cleanup, and `atomically_replaced_file` opens a same-directory temp file then renames it on clean exit and fsyncs the parent. `BaseConn.check_ok()` and `DemuxConn` implement bup's simple command response protocol, while `mux()` packages stdout/stderr packets for remote command transport. Path reducers resolve symlinks in parents, sort prefixes, and remove redundant descendants.

## State And Persistence Behavior
Module state includes `saved_errors`, cached hostname, one reusable `nullctx`, platform fsync strategy, and constants such as `sc_arg_max`. Atomic replacement creates temporary directories beside targets and persists replacements with fsync when requested. Error aggregation persists only in memory until `die_if_errors()` exits.

## Dependencies And Integration Points
It depends on `_helpers`, `bup.io`, option terminal width, and standard OS/process/mmap APIs. It is imported by most storage, metadata, index, protocol, and command modules. `BaseConn` and `DemuxConn` are protocol foundations for local/remote repo communication.

## Risks And Edge Cases
Several functions assume byte paths and POSIX behavior. `atomically_replaced_file` relies on directory file descriptors and same-directory rename semantics. `grafted_path_components()` notes possible filesystem-resolution hazards. `parse_num()` accepts floats and truncates to int. `DemuxConn` must see `BUPMUX` initialization and can raise on oversized packets. `saved_errors` is global and can leak state between operations if not cleared.

## Test Signals
`test/int/test_helpers.py`, `test/int/test_shquote.py`, `test/int/test_io.py`, `test/ext/test-get-excludes`, `test/ext/test-save-strip-graft`, `test/ext/test-main`, and many command integration tests exercise quoting, path transforms, numeric parsing, exclusion files, mux/demux behavior, and error handling.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/helpers.py -->

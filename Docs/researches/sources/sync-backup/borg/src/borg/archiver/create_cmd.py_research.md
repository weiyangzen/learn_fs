# sources/sync-backup/borg/src/borg/archiver/create_cmd.py

## Purpose

`create_cmd.py` implements `borg create`, the command that traverses filesystem inputs or command/stdin streams and writes a new archive. It handles include/exclude matching, filesystem recursion, special files, metadata collection, chunking, cache usage, progress/stat output, dry runs, and parser wiring for a large set of backup options. The source was read as a complete 1046-line file.

## Important APIs, Types, and Functions

`CreateMixIn.do_create()` is the entry point and contains `create_inner()`, which handles input modes and archive finalization. `_process_any()` dispatches a stat result to the correct `FilesystemObjectProcessors` method for regular files, directories, symlinks, FIFOs, devices, sockets, doors, and event ports, with retry logic around transient backup errors. `_rec_walk()` recursively descends directories, applies matchers, handles tagged directories and one-file-system restrictions, skips cache/repository inodes, filters dataless macOS files, opens directories safely with `OsOpen`, and records file status. `build_parser_create()` defines the command, including stdin metadata, external path sources, exclusion options, filesystem metadata toggles, cache mode, file-change detection, chunker/compression, archive tags, and path arguments.

## Control Flow

`do_create()` opens the repository for write, constructs a `PatternMatcher`, initializes output flags on `self`, records the start time, and creates a `Cache`, `Archive`, `MetadataCollector`, `ChunksProcessor`, and `FilesystemObjectProcessors` unless in dry-run mode. `create_inner()` first adds the local cache directory and local repository directory to `skip_inodes`. It then selects one of four input modes: run a content-producing command and store stdout as one file; read paths from a command, shell command, or stdin; process explicit paths including `-` as stdin; or recursively walk normal roots. After processing, non-dry-run saves the archive unless SIGINT was received, sets tags/comment/timestamp, merges stats, and emits text or JSON stats.

## State and Persistence Behavior

Successful non-dry-run execution writes a new archive into the repository, updates the manifest through `archive.save()`, writes file metadata and content chunks through the cache/chunker pipeline, and updates files-cache state according to `--files-cache`. Dry-run avoids archive/cache writes but still stats and walks inputs. External command modes spawn subprocesses; `--content-from-command` prevents archive creation if the command exits nonzero after piping, while plain stdin piping cannot observe the producer's exit status. Warnings are recorded for per-item backup errors, and file status counters update for processed items.

## Dependencies and Integration Points

The command integrates deeply with `Archive`, `Cache`, `FilesystemObjectProcessors`, `MetadataCollector`, `ChunksProcessor`, `PatternMatcher`, `backup_io`, `OsOpen`, `stat_update_check`, filesystem helpers (`os_stat`, `get_strip_prefix`, `slashify`, `dir_is_tagged`, platform flags), subprocess environment preparation, and JSON/stat formatting helpers. It also shares parser conventions with help text, completion support, and exclusion groups from `_common`.

## Risks and Edge Cases

Key risks include filesystem races between stat/open/read, files changing during backup, permission errors, recursive loops or duplicate roots avoided through `skip_inodes`, accidentally backing up the repository/cache, path normalization and slashdot prefix stripping, shell-command injection inherent to explicit `--paths-from-shell-command`, special-device reads when `--read-special` is enabled, dataless cloud files materializing unless filtered before open, and differing ctime semantics on Windows. `_process_any()` retries transient backup errors but intentionally does not retry permission errors.

## Test Signals

Tests should cover normal recursion, dry-run/list/filter output, `-` stdin, `--content-from-command` success and nonzero failure, `--paths-from-stdin` with custom delimiters, shell and non-shell path commands, slashdot stripping, exclude/include/tagged directory behavior, one-file-system recursion, skipping cache/repository inodes, symlink and `--read-special` handling, dataless file filtering, Windows `files_changed=ctime` fallback, retry paths for transient `BackupOSError`, file-changed warnings, JSON stats, and SIGINT avoiding archive save.

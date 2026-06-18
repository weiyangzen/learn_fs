# sources/sync-backup/borg/src/borg/archiver/recreate_cmd.py

## Purpose

`recreate_cmd.py` implements `borg recreate`, rebuilding existing archives with optional filtering, rechunking, recompression, comment/timestamp changes, and target archive naming. It is a potentially destructive archive transformation command. The source was read as a complete 175-line file.

## Important APIs, Types, and Functions

`RecreateMixIn.do_recreate()` builds a matcher, configures `ArchiveRecreater`, selects archive candidates, skips temporary recreate archives, chooses target/delete-original behavior, calls `recreater.recreate()`, and writes the manifest. `build_parser_recreate()` wires list/filter/dry-run/stats options, exclusion groups, archive filters, `--target`, `--comment`, `--timestamp`, `--compression`, `--chunker-params`, and path arguments.

## Control Flow

The command opens the repository with cache and check compatibility. It builds a matcher from archive-internal paths and patterns, stores list/filter output flags on `self`, and constructs an `ArchiveRecreater` with exclusion tag settings, chunker params, compression, progress, stats, file-status printer, dry-run, and timestamp. It iterates `manifest.archives.list_considering(args)`, filters protected archives, skips temporary archive names, prints the archive being processed, and recreates either in place or to `--target`. If no changes are needed, it logs a skip. Non-dry-run writes the manifest after processing.

## State and Persistence Behavior

Non-dry-run recreate writes new archive metadata and chunks, may delete or replace the original archive entry when no target is specified, and can permanently remove files from archives according to filters after compaction. Dry-run avoids repository changes. Temporary archives named by `ArchiveRecreater` exist during operation and are skipped if encountered in the candidate list.

## Dependencies and Integration Points

The module is a thin command layer over `ArchiveRecreater` from `archive`, and depends on matcher/exclusion helpers, archive filters, validators for archive names/comments/timestamps/chunker/compression, manifest writing, and status printing shared with create. It interacts with compact because replaced/deleted archive data does not free space until compaction.

## Risks and Edge Cases

Filtering semantics apply to archived paths, not local filesystem paths, so absolute patterns do not match as users may expect. Rechunking can require large temporary space and may worsen data loss if chunks are already missing. `--target` creates a new archive instead of replacing originals; without it, originals are removed only after successful recreation. Multiple input archives with a single `--target` would rely on lower-level duplicate-name handling and should be treated carefully.

## Test Signals

Tests should cover dry-run/list/filter behavior, in-place recreation, target recreation, comment/timestamp changes, recompression and rechunking, path/exclusion filtering, protected archives, temporary archive skipping, no-op skip logging, manifest write behavior, and missing-chunk/rechunk warnings through integration tests.

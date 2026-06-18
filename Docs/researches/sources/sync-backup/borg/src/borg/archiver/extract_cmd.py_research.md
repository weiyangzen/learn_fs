# sources/sync-backup/borg/src/borg/archiver/extract_cmd.py

## Purpose

`extract_cmd.py` implements `borg extract`, restoring archive contents into the current working directory or stdout. It handles path filtering, strip-components, dry-run, sparse extraction, hard links, progress accounting, and delayed directory permission restoration. The source was read as a complete 191-line file.

## Important APIs, Types, and Functions

`ExtractMixIn.do_extract()` is wrapped by `with_repository` and `with_archive`. It uses `build_matcher()` for path/pattern selection, `build_filter()` for progress size calculation with stripping, `HardLinkManager` for hardlink identity tracking, `ProgressIndicatorPercent` for extraction and permission progress, and `archive.extract_item()` for actual restoration. `build_parser_extract()` wires list/dry-run/numeric metadata flags, `--stdout`, `--sparse`, `--continue`, archive name, paths, and exclusion options.

## Control Flow

The command first warns if the filesystem encoding is ASCII. It builds a matcher, initializes options and a directory stack, and optionally computes total extracted size by iterating matching archive items. It then iterates all archive items in archive order. For each item it applies `strip_components`, logs list output with `+` or `-`, and if matched extracts it. Directories are extracted immediately with attributes deferred, pushed onto a stack, and finalized after children are processed. Non-directories are extracted with sparse/hardlink/progress/continue settings. At the end, remaining directories are extracted again to restore attributes, unmatched include patterns are warned, and progress output is cleared.

## State and Persistence Behavior

Non-dry-run extraction writes files, directories, links, device metadata, xattrs, ACLs, flags, and permissions into the current working directory unless `--stdout` changes data output. Dry-run still reads archive metadata/data enough to validate extraction but does not write files. `--continue` permits continuing interrupted extraction for the same archive. Directory attributes are deliberately restored last to avoid permission modes preventing child creation.

## Dependencies and Integration Points

This command depends on archive extraction behavior, platform metadata restoration options controlled by parsed args, hardlink management, matcher/filter helpers, progress display, and warning types. It integrates with `list_cmd.py` and `create_cmd.py` semantics for path matching and item status display.

## Risks and Edge Cases

Extraction always targets the current working directory, so caller cwd matters. ASCII filesystem encoding cannot represent non-ASCII archive paths. `strip_components` can skip items entirely if no path remains. Parent directories omitted by filtering cannot have metadata restored. Symlink behavior is handled by archive extraction and can affect visible paths. Errors per item are warnings, so extraction can complete partially.

## Test Signals

Tests should cover full and partial extraction, dry-run, list markers, strip-components skipping and renaming, directory attribute restoration order, hardlinks, sparse files, stdout extraction, continue mode after interruption, unmatched include warnings, ASCII encoding warnings, and per-item `BackupError` warnings without total abort.

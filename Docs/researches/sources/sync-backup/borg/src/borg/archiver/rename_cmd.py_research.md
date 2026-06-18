# sources/sync-backup/borg/src/borg/archiver/rename_cmd.py

## Purpose

`rename_cmd.py` implements `borg rename`, changing an archive's name. Renaming creates a different archive ID because archive metadata changes. The source was read as a complete 37-line file.

## Important APIs, Types, and Functions

`RenameMixIn.do_rename()` is wrapped with repository/cache/check compatibility and `with_archive`; it calls `archive.rename(args.newname)` and writes the manifest. `build_parser_rename()` registers old and new archive names using `archivename_validator`.

## Control Flow

The decorators resolve the repository, manifest, cache, and current archive from `OLDNAME`. The method delegates the actual rename to the `Archive` instance, then persists the manifest. Parser setup provides a short epilog and two required positional names.

## State and Persistence Behavior

The command mutates archive metadata and manifest state. Because the archive ID changes, downstream references by ID and cached metadata may need to observe the new ID. It does not directly delete content chunks.

## Dependencies and Integration Points

It depends on `with_archive`, `Archive.rename()`, manifest writing, and archive-name validation. It is the simplest command layer for archive metadata mutation and shares check compatibility with recreate/key operations.

## Risks and Edge Cases

Name validation happens at parse time, but duplicate names or repository-specific conflicts are handled by lower layers. Partial failure between `archive.rename()` and `manifest.write()` would be critical, so integration tests should use the real archive implementation. Users relying on old archive IDs must understand ID changes.

## Test Signals

Tests should verify successful rename changes archive name and ID, manifest persistence, missing old-name errors via `with_archive`, invalid new names rejected by parser, and duplicate/conflicting target handling from archive internals.

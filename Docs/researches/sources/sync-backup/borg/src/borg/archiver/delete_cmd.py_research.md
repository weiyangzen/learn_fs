# sources/sync-backup/borg/src/borg/archiver/delete_cmd.py

## Purpose

`delete_cmd.py` implements `borg delete`, which soft-deletes one or more archives from a repository. It intentionally does not free repository object storage; users must later run `borg compact`. The source was read as a complete 94-line file.

## Important APIs, Types, and Functions

`DeleteMixIn.do_delete()` loads the manifest, resolves either a single archive name or archive-filtered list, excludes protected archives tagged `@PROT`, soft-deletes archive IDs with `manifest.archives.delete_by_id()`, optionally lists results, and writes the manifest. `build_parser_delete()` wires `--dry-run`, `--list`, archive filters, and optional `NAME`.

## Control Flow

The command opens the repository with `manifest=False`, then explicitly loads the manifest for delete compatibility. It determines the candidate archives, filters protected archives, aborts if the user selected all archives without an explicit name or match pattern, and iterates candidates. Each archive is formatted before deletion for output stability. Non-dry-run deletes by ID; dry-run only logs what would happen. If at least one archive was deleted, the manifest is written and a compact reminder is emitted.

## State and Persistence Behavior

The command mutates only manifest archive metadata by marking/removing archive entries according to Borg's soft-delete mechanism. It does not delete content chunks or free disk space. Dry-run makes no repository changes. The operation is a precursor to `compact_cmd.py`, which permanently removes soft-deleted archive entries and unreferenced objects.

## Dependencies and Integration Points

Dependencies include `Manifest`, archive filter helpers from `_common`, `format_archive()`, `archivename_validator`, and `bin_to_hex()`. It integrates with `undelete` semantics through soft deletion and with `compact` for final space reclamation.

## Risks and Edge Cases

The safety guard prevents accidental deletion of every archive unless a name or archive match is explicit. Protected archives are silently excluded from candidates. Corrupt archive metadata is handled by deleting manifest entries by ID rather than constructing full `Archive` objects. A `KeyError` during deletion produces a warning but does not abort all candidates.

## Test Signals

Tests should cover single-name deletion, filter-based deletion, dry-run/list output, all-archive safety abort, protected `@PROT` archives, already-missing archive IDs, manifest write only after actual deletion, and the compact reminder after successful mutation.

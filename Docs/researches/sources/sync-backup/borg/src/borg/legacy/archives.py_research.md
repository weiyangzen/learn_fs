# sources/sync-backup/borg/src/borg/legacy/archives.py

## Purpose
Manages Borg 1.x archive registries embedded in legacy manifest blobs. It adapts old `{name: {"id": bytes, "time": str}}` storage to the modern archive listing interface used during transfer and compatibility operations.

## Important APIs, Types, And Functions
`LegacyArchives` provides `prepare`, `finish`, `ids`, `_get_archive_meta`, `_infos`, `_info_tuples`, `_matching_info_tuples`, `count`, `names`, `exists`, `get`, `get_by_id`, `create`, `list`, `list_considering`, `get_one`, `_set_raw_dict`, and `_get_raw_dict`. Several soft-delete methods intentionally raise `NotImplementedError`.

## Control Flow
`prepare` loads the raw manifest archive dict; `finish` returns a `StableDict` for deterministic manifest serialization. Listing converts raw entries to `ArchiveInfo`, optionally loads archive metadata from the repository, filters by archive id prefix, tags, user, host, or name pattern, applies date filters, sorts by requested keys, slices first/last, and reverses if requested.

## State And Persistence
`_archives` is an in-memory dict mirroring legacy manifest state. `finish` hands it back for manifest persistence. `_get_archive_meta` reads archive metadata objects from the legacy repository and reports a placeholder for missing objects.

## Dependencies And Integration Points
Used by manifest initialization for `LegacyRepository`. Depends on legacy repository object retrieval, manifest repo object parser, key unpacking, `ArchiveItem`, pattern translation, date filtering from modern manifest code, and parse/time helpers.

## Risks And Edge Cases
Some modern archive APIs are unsupported for Borg 1.x repositories. Archive ID matching must match exactly one archive. Missing archive metadata is represented as a fake non-existing archive. Sorting keys must exist on `ArchiveInfo`. `list_considering` rejects combining a specific name with list filters.

## Test Signals
Existing legacy archive tests should cover raw dict round-trip, create overwrite behavior, get by name/id, match filters, id prefix ambiguity, tags/user/host/name filtering, date filtering, sorting/slicing/reverse, missing archive object placeholder, and unsupported delete APIs.

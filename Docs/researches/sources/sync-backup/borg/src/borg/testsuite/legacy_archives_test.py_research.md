# sources/sync-backup/borg/src/borg/testsuite/legacy_archives_test.py

Purpose: tests `LegacyArchives`, Borg 1.x manifest archive listing compatibility, archive metadata loading, filtering, and manifest dispatch for legacy repositories.

Important APIs and control flow: helper factories build mock archive dictionaries, `ArchiveInfo` objects, and controlled list targets. Tests cover initialization, raw dict get/set, prepare/finish, IDs/count/names, existence, creation with string or datetime timestamps, overwrite, lookup by name/id, raw output, and unsupported id-based mutation methods raising `NotImplementedError`. `_get_archive_meta` is tested for repository object missing, successful parse/unpack through `ArchiveItem`, and bad metadata version. Listing tests cover sorting, reverse, first/last slicing, date filtering delegation, match filters for name/user/host/tags/archive-id prefix, ambiguous IDs, `get_one`, and `list_considering` argument validation/delegation. Final tests assert `LegacyArchives` satisfies `ArchivesInterface` and that `Manifest` creates it for a legacy repository subclass.

State and persistence: mostly mocked in-memory repository/manifest state. Archive dictionaries store ids and ISO timestamps. Metadata loading simulates repository object reads through mocks.

Dependencies and integration points: depends on `LegacyArchives`, `LegacyRepository`, `Manifest`, `ArchiveInfo`, `ArchivesInterface`, `PlaintextKey`, CLI `Namespace`, and error classes. It is the compatibility layer between Borg 1.x manifests and Borg 2 archive interfaces.

Risks: many methods are intentionally not implemented for legacy archives; callers must not assume full modern archive mutation support. Archive ID prefix matching can be ambiguous and must error.

Test signals: exact dict/list outputs, `ArchiveInfo` instances, delegated filters, command errors on 0/multiple matches, and manifest dispatch to legacy archive interface.

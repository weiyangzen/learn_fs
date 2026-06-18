# sources/object-store/rustfs/crates/filemeta/src/filemeta/inline_data.rs

Purpose: data-directory and inline-data helper methods for `FileMeta`.

Important APIs/functions: `find_unshared_data_dir_for_version`, `shard_data_dir_count`, `get_data_dirs`, and `shared_data_dir_count`.

Control flow: helpers scan shallow object versions whose headers indicate object type and data-dir usage. They decode each data dir from serialized version metadata only when needed. `find_unshared_data_dir_for_version` returns the target version's data dir only if no other version shares it. `shared_data_dir_count` treats existing inline data for the version as not sharing a disk data dir and otherwise counts other object versions with the same decoded directory.

State and persistence: no writes. The functions inspect persisted version metadata and inline-data entries to decide whether disk data directories can be safely reclaimed or are shared by multiple versions.

Dependencies and integration: depends on `VersionType`, `FileMetaVersion::decode_data_dir_from_meta`, `InlineData`, `Uuid`, and `HashSet`. It is called by deletion/transition logic in `filemeta.rs`.

Risks: decode failures are mostly collapsed with `unwrap_or_default`, which can hide malformed metadata and return `None` instead of surfacing corruption. Correct reclamation depends on version headers accurately setting `UsesDataDir`. Inline-data short-circuit means delete logic must keep inline and data-dir states mutually consistent.

Test signals: tests create two versions with restore metadata and erasure info, then assert unique data dirs are returned and shared data dirs return `None`.

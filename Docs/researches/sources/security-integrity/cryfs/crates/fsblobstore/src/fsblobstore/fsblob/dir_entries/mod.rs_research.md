# sources/security-integrity/cryfs/crates/fsblobstore/src/fsblobstore/fsblob/dir_entries/mod.rs

Purpose: Facade for directory entry submodules.

Important APIs/types/functions: declares `atime_update_behavior`, `entry`, and `entry_list`; re-exports `AtimeUpdateBehavior`, `DirEntry`, `EntryType`, `DirEntryList`, serialization result, and directory mutation error enums.

Control flow: none. It preserves a clean API boundary around serialized entry internals.

State and persistence behavior: no state; the re-exported types define directory persistence through `DirEntryList`.

Dependencies and integration points: used by `dir_blob.rs` and re-exported by `fsblob/mod.rs` for higher layers.

Risks: exposing `DirEntryList` along with error enums means downstream code can rely on low-level behavior, so facade changes are API-sensitive.

Test signals: compile coverage plus all `DirBlob`/`DirEntryList` tests.

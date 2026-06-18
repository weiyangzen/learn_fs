# sources/storage-engines/tikv/components/sst_importer/src/caching/mod.rs

Purpose: module declaration for importer caching helpers.

Important APIs: exposes `cache_map` and `storage_cache` modules within the crate.

Control flow, state, and integration: no runtime logic. It groups the generic cache map and external-storage pool cache implementation used by SST importer download/apply paths.

Risks: minimal; module visibility changes affect internal imports.

Test signals: tests live in `cache_map.rs`.

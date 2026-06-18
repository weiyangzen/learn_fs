# sources/storage-engines/tikv/components/sst_importer/src/lib.rs

Purpose: crate root for SST importer functionality.

Important APIs: enables nightly `min_specialization` and `error_reporter`, imports serde derive and TiKV macros, declares internal modules (`config`, `errors`, `import_file`, `sst_merge_iter`, `sst_writer`, `util`, `caching`) and public modules (`import_mode`, `import_mode2`, `metrics`, `sst_importer`). Re-exports core API: `Config`, `ConfigManager`, `Error`, `Result`, `error_inc`, `API_VERSION_2`, `sst_meta_to_path`, `range_overlaps`, `SstImporter`, `BinaryIterator`, `RawSstWriter`, `TxnSstWriter`, `copy_sst_for_ingestion`, and `prepare_sst_for_ingestion`.

Control flow, state, and integration: no direct runtime logic. It defines the public crate surface consumed by TiKV server, import services, and tests.

Dependencies and integration points: `server2.rs` imports `ImportSstService` and `SstImporter` through TiKV, while this crate exports lower-level importer building blocks.

Risks: public re-export changes are breaking for downstream modules. Nightly feature usage ties the crate to compiler capabilities.

Test signals: tests live in module files.

# sources/storage-engines/tikv/components/engine_panic/src/import.rs

Purpose: Panic skeleton for external SST ingestion.

Important APIs and types: `PanicEngine` implements `ImportExt` with associated `PanicIngestExternalFileOptions`. Options implement `new`, `move_files`, and `allow_write`.

Control flow and state: Ingest, latch acquisition, and option mutation all panic. No latch or ingest state exists.

Dependencies and integration: References `RangeLatchGuard`, `Range`, and `IngestExternalFileOptions`, documenting the contract real engines must satisfy for import/restore paths.

Risks: Runtime use panics.

Test signals: No tests.

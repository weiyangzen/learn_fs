# sources/storage-engines/tikv/components/engine_traits/src/import.rs

Purpose: Abstracts ingestion of external SST files into an engine.

Important APIs and control flow: `ImportExt` associates `IngestExternalFileOptions`, ingests files into a CF with optional range and forced allow-write mode, and acquires a range latch for ingestion serialization. `IngestExternalFileOptions` controls move-files and allow-write behavior.

State, persistence, and dependencies: Ingestion moves or links external SST data into persistent engine storage and may lock a key range during the operation.

Integration points, risks, and test signals: Used by snapshot apply, import, backup restore, and range delete by writer. Risks include overlapping writes when allow-write is enabled, latch misuse, partial ingestion failures, encryption metadata, and CF/range mismatch. Signals come from backend ingestion and SST tests.

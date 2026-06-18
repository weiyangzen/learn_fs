<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/error_code/src/engine.rs -->
# sources/storage-engines/tikv/components/error_code/src/engine.rs

Purpose: this module declares storage-engine abstraction error codes under `KV:Engine:`.

Important APIs and constants: constants include `ENGINE`, `NOT_IN_RANGE`, `PROTOBUF`, `IO`, `CF_NAME`, `CODEC`, `DATALOSS`, `DATACOMPACTED`, and `BOUNDARY_NOT_SET`, plus the generated `ALL_ERROR_CODES`.

Control flow and state: there is no runtime logic besides lazy vector initialization. No `ErrorCodeExt` implementation appears here; engine error types must map to these constants elsewhere.

Dependencies and integration points: these codes sit under the `engine_traits`/engine abstraction layer and are expected to be used by RocksDB, raft-engine, and related wrappers when exposing common error categories to upper layers. The generator binary includes this module.

Risks: empty descriptions and workarounds make the code strings the only catalog payload. The typo-like suffix `DATACOMPACTED` differs from `DATA_COMPACTED` in the PD namespace, so cross-subsystem normalization must be deliberate.

Test signals: no local tests exist. The crate-level macro test validates the expansion pattern used here.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/error_code/src/engine.rs -->

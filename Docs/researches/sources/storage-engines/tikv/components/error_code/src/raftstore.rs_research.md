<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/error_code/src/raftstore.rs -->
# sources/storage-engines/tikv/components/error_code/src/raftstore.rs

Purpose: this module defines raftstore error codes under `KV:Raftstore:` and maps `kvproto::errorpb::Error` protobuf payloads to stable codes.

Important APIs and constants: the namespace includes region/leader errors (`NOT_LEADER`, `REGION_NOT_FOUND`, `KEY_NOT_IN_REGION`, `EPOCH_NOT_MATCH`), store/transport errors (`DISK_FULL`, `STORE_NOT_MATCH`, `TRANSPORT`, `TIMEOUT`), command state errors (`STALE_COMMAND`, `READ_INDEX_NOT_READY`, `PROPOSAL_IN_MERGING_MODE`, `DATA_IS_NOT_READY`), flashback/recovery/witness errors, and snapshot errors (`SNAP_ABORT`, `SNAP_TOO_MANY`, `SNAP_UNKNOWN`). `ALL_ERROR_CODES` is generated.

Control flow: `impl ErrorCodeExt for errorpb::Error` checks `has_*` fields in priority order and returns the first matching code. The order matters when a protobuf contains multiple sub-errors. Several declared constants, such as `PENDING_PREPARE_MERGE`, `MISMATCH_PEER_ID`, and snapshot codes, are not covered by the conversion function, likely because they map from other error types.

State and persistence behavior: no mutable state exists beyond the lazy catalog vector. Conversion is read-only over the protobuf message.

Dependencies and integration points: it depends on `kvproto::errorpb` and is central to client-visible raftstore error reporting. The generator binary includes this module.

Risks: unmapped declared constants and fallback to `UNKNOWN` can hide precise protobuf fields if new `errorpb::Error` variants are added without updating the match chain. The priority order should be treated as part of the contract. Descriptions are empty, so downstream UX relies on code names.

Test signals: there are no tests in this file for the `has_*` mapping order. Compile-time availability of protobuf methods is the main signal.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/error_code/src/raftstore.rs -->

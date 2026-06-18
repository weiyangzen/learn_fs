<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/error_code/src/raft.rs -->
# sources/storage-engines/tikv/components/error_code/src/raft.rs

Purpose: this module defines `KV:Raft:` error-code constants and maps `raft::Error` variants to them via `ErrorCodeExt`.

Important APIs and constants: constants include `IO`, `STORE`, `STEP_LOCAL_MSG`, `STEP_PEER_NOT_FOUND`, `PROPOSAL_DROPPED`, `CONFIG_INVALID`, `CODEC_ERROR`, `EXISTS`, `NOT_EXISTS`, and `CONF_CHANGE_ERROR`. The `impl ErrorCodeExt for raft::Error` matches each current variant to its corresponding constant.

Control flow: `error_code()` is a direct `match` over raft errors. `Error::RequestSnapshotDropped` is marked `unreachable!()`, implying the TiKV call paths using this conversion should never observe that variant or should handle it earlier.

State and persistence behavior: the module has no persistent state. The lazy `ALL_ERROR_CODES` vector is used for enumeration, while conversion is stateless.

Dependencies and integration points: it depends on the external `raft` crate and the crate-local `ErrorCodeExt`. It is consumed by raftstore or engine code that propagates raft library errors through TiKV's error-code system. The generator binary includes this module.

Risks: the `unreachable!()` arm can panic if upstream raft starts returning `RequestSnapshotDropped` through a path that calls `error_code()`. Any new `raft::Error` variants require updating this match or compilation will fail. Descriptions and workarounds remain empty.

Test signals: there are no local tests for the mapping. Exhaustiveness of the match is a compile-time signal for most variants.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/error_code/src/raft.rs -->

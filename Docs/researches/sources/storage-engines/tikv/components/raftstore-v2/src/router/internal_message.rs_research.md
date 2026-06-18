# sources/storage-engines/tikv/components/raftstore-v2/src/router/internal_message.rs

Purpose: this file defines messages and result structs exchanged between peer FSMs and apply FSMs.

Important APIs/types/functions: `ApplyTask` variants are committed entries, snapshot generation, unsafe write bytes, manual flush, bucket-stat refresh, and capture-apply. `ApplyRes` reports applied index/term, admin results, modification trace, apply metrics, bucket stats, and SST applied indexes. `SstApplyIndex` identifies a CF index and raft index for SST application tracking.

Control flow: peer FSM sends `ApplyTask` to apply workers; apply workers send `ApplyRes` back through router messages after applying committed entries or internal tasks. Snapshot generation tasks come from `snapshot.rs`, while capture tasks are CDC-related.

State and persistence: these are transport structs only. `ApplyRes.modifications` and `sst_applied_index` carry persistence/flush tracking signals to peer-side state.

Dependencies/integration: depends on PD bucket stat types, raftstore apply metrics, command/admin result types, committed entries, data trace, and `GenSnapTask`.

Risks: adding apply task variants requires peer and apply dispatch updates. Missing fields in `ApplyRes` can desynchronize log GC, flow control, or callbacks.

Test signals: no local tests; compile-time exhaustiveness and apply/peer integration tests cover message use.

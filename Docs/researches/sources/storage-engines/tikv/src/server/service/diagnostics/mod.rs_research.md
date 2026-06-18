# sources/storage-engines/tikv/src/server/service/diagnostics/mod.rs

Purpose: exposes the gRPC Diagnostics service by composing log search and host telemetry collectors.

Important APIs/types/functions: `Service`; `SYS_INFO`; `search_log`; `server_info`; modules `log` and `sys`.

Control flow: `search_log` selects normal or slow log path from request target, spawns `log::search`, maps responses to buffered gRPC writes, streams them to the sink, and logs errors. `server_info` captures baseline CPU/NIC/IO snapshots for load requests, waits about one second on the global timer, collects hardware/load/system info according to `ServerInfoType`, sorts results by type/name, and replies.

State/persistence: runtime-only global `SYS_INFO` mutex over `sysinfo::System`; no persistent writes. Load info samples twice to compute deltas.

Dependencies/integration: grpcio Diagnostics trait, Tokio handle, global timer, `sysinfo`, `sys::load_info/hardware_info/system_info`, and `log::search`. Risks include global lock contention, unwraps around spawned task joins, expensive `All` system collection, and limited handling for enum variants. Tests live in `log.rs` and `sys.rs`.

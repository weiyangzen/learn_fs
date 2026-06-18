# sources/storage-engines/tikv/src/server/resolve.rs

Purpose: asynchronously resolves store IDs to raft peer addresses through PD, caches addresses, and updates global replication group/label state for raft transport.

Important APIs/types/functions: `StoreAddrResolver`; `PdStoreAddrResolver`; `new_resolver`; `Runner::{resolve, get_address}`; `Task`; `MockStoreAddrResolver`; `store_address_refresh_interval_secs`.

Control flow: resolver tasks run on a worker. `resolve` returns cached addresses younger than 60 seconds unless failpoints override the interval. On cache miss/stale entry, `get_address` fetches PD store metadata. Tombstone or "not found" conditions increment metrics, report maybe-tombstone through raft extension, and return `StoreTombstone`. DR auto-sync mode registers store labels and reports resolved group id; normal mode backs up labels. Peer address is preferred and empty addresses are rejected.

State/persistence: in-memory address cache and `GlobalReplicationState`; PD remains authoritative. Tombstone/resolved reports are side effects to raftstore.

Dependencies/integration: used by raft client connection builder/server transport; depends on PD client, worker scheduler, replication state, metrics, and raft extension. Risks include string matching for "not found", stale cache window, empty-address test workaround, and callback execution on resolver worker. Tests cover store states, not-found, peer-address preference, and cache refresh.

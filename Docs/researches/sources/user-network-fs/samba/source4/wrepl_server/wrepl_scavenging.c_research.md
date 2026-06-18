<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/wrepl_server/wrepl_scavenging.c -->
# sources/user-network-fs/samba/source4/wrepl_server/wrepl_scavenging.c

## Purpose

This file scavenges expired WINS records for the WREPL server. It transitions owned records through active/released/tombstone/deleted states, cleans non-active replica records, verifies expired active replica records with the owning WINS server, and schedules future scavenging.

## Important APIs, Types, and Functions

- `wreplsrv_owner_filter()` builds LDB filters for local owner versus remote owners, treating `0.0.0.0` as local-owned only.
- `wreplsrv_scavenging_owned_records()` handles expired local-owned records.
- `wreplsrv_scavenging_replica_non_active_records()` handles expired released/tombstone replica records.
- `wreplsrv_scavenging_replica_active_records()` starts async verification for expired active replica records.
- `verify_handler()` processes challenge results and modifies/deletes/skips records.
- `wreplsrv_scavenging_run()` gates scheduling, first-run skip, and the three scavenging passes.

## Control Flow

`wreplsrv_scavenging_run()` returns early until `next_run` expires, schedules the next run, skips actual scavenging on the first startup call, and prevents reentry with `service->scavenging.processing`. Owned scavenging searches expired local-owner records. Static active records are refreshed; normal active records become released, or special groups with propagation enabled may remain active/tombstone depending on replica addresses; released records become tombstones; tombstones are deleted only after `tombstone_extra_timeout` since startup.

Replica non-active scavenging transitions released replicas to tombstones and later deletes tombstones. Replica active scavenging asks the owning WINS server through `nbtd_proxy_wins_challenge`; missing records are deleted, matching records are refreshed, and different address replies tombstone the record with local ownership/version allocation.

## State and Persistence Behavior

The file modifies persistent `winsdb` records: state, expiration times, address expiration times, ownership, allocated version IDs, and deletions. It updates `service->scavenging.next_run` and `processing`. Active replica verification is asynchronous and keeps `verify_state` alive under the service until callbacks complete.

## Dependencies and Integration Points

Dependencies include WINS DB LDB searches and record APIs, WREPL state/type constants, tevent/IRPC calls to `nbt_server`, time helpers, service config intervals, and loadparm option `wreplsrv:propagate name releases`. Periodic scheduling calls this module before pull/push replication.

## Risks and Edge Cases

The owned-record loop reuses loop variable `i` inside the special-group address scan, which can disturb the outer result iteration. Verification uses a simplified WINS name challenge rather than a full Windows-style WREPL/DCERPC verification. Async verification errors generally skip changes, allowing stale replicas to remain until a later pass. First-run scavenging intentionally skips to avoid aggressive startup deletion.

## Test Signals

Signals include correct time-gated execution, active-to-released/tombstone transitions, delayed tombstone deletion after startup extra timeout, static record refresh, propagated special-group behavior when enabled, replica verification refresh/delete/tombstone outcomes, and no concurrent scavenging reentry.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/wrepl_server/wrepl_scavenging.c -->

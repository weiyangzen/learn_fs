<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/wrepl_server/wrepl_out_helpers.c -->
# sources/user-network-fs/samba/source4/wrepl_server/wrepl_out_helpers.c

## Purpose

This file provides asynchronous outbound WREPL helper state machines: connect/associate to partners, pull owner tables, pull changed names, run a full pull cycle applying records, and notify partners through update/inform push messages.

## Important APIs, Types, and Functions

- `wreplsrv_out_connect_send/recv()` connects to a partner, performs WREPL association, and caches push/pull connections where appropriate.
- `wreplsrv_pull_table_send/recv()` obtains a remote owner table or uses an inform-supplied table.
- `wreplsrv_pull_names_send/recv()` requests names for one owner/version range.
- `wreplsrv_pull_cycle_send/recv()` coordinates table update, per-owner name pulls, `wreplsrv_apply_records()`, and optional association stop.
- `wreplsrv_push_notify_send/recv()` sends WREPL update/inform notifications and handles update stream role reversal.

## Control Flow

Every operation is represented by a `composite_context` plus a private stage enum. Connect starts `wrepl_connect_send()`, then `wrepl_associate_send()`, stores peer association context/version, and optionally caches the connection in `partner->push.wreplconn` or `partner->pull.wreplconn`. Pull table either returns the supplied inform table immediately or connects and sends a table query. Pull cycle updates `partner->pull.table`, then walks owners whose remote max version is newer than local, pulls names with `min_version = local + 1`, applies records, and repeats. If the cycle was initiated on an already-donated stream, it sends association stop at the end.

Push notify chooses inform/update command based on `inform` and `propagate` flags, falls back from inform to update for old peers, fills the local table, sends the request, and for update messages splits the client socket stream and merges it into an inbound server connection for the peer's send requests.

## State and Persistence Behavior

The helpers maintain cached outbound connections on partners, association context fields, partner pull tables, pending composite requests, and pulled name batches. Persistent WINS DB changes happen through `wreplsrv_apply_records()`. Push update can transfer stream ownership to an inbound connection and free the outbound connection.

## Dependencies and Integration Points

Dependencies include WREPL client functions, composite/tevent async APIs, WINS DB and WREPL table helpers, address selection via `wrepl_best_ip()`, `wreplsrv_in_connection_merge()`, and the record application layer. It is used by inbound update handling and by periodic pull/push schedulers.

## Risks and Edge Cases

Connection caching must discard disconnected cached sockets. Pull cycle compares owner max versions and skips local/self owners; stale tables can miss changes until refreshed. The TODO notes record application may need async handling because conflict resolution can trigger network access. Update/inform fallback depends on peer major version. Stream split/merge errors can leave push updates incomplete.

## Test Signals

Signals include successful connection association, correct connection caching, accurate remote table ingestion, pulls only for owners with newer versions, successful record application and owner-table updates, association stop on donated streams, inform/update fallback for older peers, and conversion from outbound update to inbound server role.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/wrepl_server/wrepl_out_helpers.c -->

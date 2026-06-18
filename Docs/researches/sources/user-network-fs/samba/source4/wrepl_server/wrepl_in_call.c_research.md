<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/wrepl_server/wrepl_in_call.c -->
# sources/user-network-fs/samba/source4/wrepl_server/wrepl_in_call.c

## Purpose

This file handles decoded inbound WINS Replication protocol calls. It manages association start/stop, validates association contexts, authorizes partner direction, serves owner-table and name-send requests, reacts to update/inform messages, and constructs reply packets.

## Important APIs, Types, and Functions

- `wreplsrv_in_start_association()` and `wreplsrv_in_stop_association()` maintain association context state.
- `wreplsrv_in_table_query()` fills a local WREPL owner table reply.
- `wreplsrv_record2wins_name()` converts `winsdb_record` to `wrepl_wins_name`.
- `wreplsrv_in_send_request()` queries `winsdb` for active/tombstone records in a version range and returns sorted names.
- `wreplsrv_in_update()` donates the accepted stream to an outbound pull cycle.
- `wreplsrv_in_inform()` triggers an outbound pull based on a partner-supplied table.
- `wreplsrv_in_replication()` dispatches replication commands and enforces partner type flags.
- `wreplsrv_in_call()` is the top-level dispatcher.

## Control Flow

The dispatcher rejects invalid message types, handles initial invalid-association behavior, and appends standard opcode bits plus peer association context on successful replies. Replication commands first validate association bits when present, then lazily resolve the remote peer as a configured partner by IPv4 address. Non-partners or partners using the wrong push/pull direction receive stop-association behavior.

Table queries call `wreplsrv_fill_wrepl_table()`. Send requests normalize max version `0` to `UINT64_MAX`, validate ranges, search the WINS LDB for records owned by the requested owner and in active/tombstone states, parse records, skip records that became expired during parsing, sort by version ID, and return them. Update messages convert the inbound connection into a client-side `wreplsrv_out_connection` and start `wreplsrv_pull_cycle_send()` on the same stream.

## State and Persistence Behavior

Association state is held on `wreplconn->assoc_ctx`. Send requests are read-only against `winsdb`, but parsing can observe time-based state changes. Update/inform can initiate outbound pull cycles that later mutate the local WINS DB. The update path steals table partner arrays and donates stream ownership.

## Dependencies and Integration Points

Dependencies include WREPL client/server helpers, WINS DB APIs, LDB searches, owner-table helpers, `wreplsrv_pull_cycle_send()`, `wreplsrv_out_partner_pull()`, and Samba talloc/tevent infrastructure. It is called from `wrepl_in_connection.c` after packet decoding.

## Risks and Edge Cases

Version compatibility code intentionally ignores start-association version fields for NT4 compatibility. Returning `ERROR_INVALID_PARAMETER` is used as "ignore/no reply" behavior in several paths. Partner type enforcement is critical; misconfiguration blocks replication. The update path frees the send queue and donates the stream, so later inbound connection handling must stop using it.

## Test Signals

Signals include correct association replies, stop behavior, empty replies for unknown owners or invalid ranges, sorted send replies, rejection of non-partners/wrong-direction partners, successful pull-cycle handoff on update, and no reply for inform messages.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/wrepl_server/wrepl_in_call.c -->

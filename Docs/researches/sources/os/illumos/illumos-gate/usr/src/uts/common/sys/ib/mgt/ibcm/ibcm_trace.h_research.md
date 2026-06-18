# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/mgt/ibcm/ibcm_trace.h

## Scope

Defines internal per-connection tracing support for IBCM RC connection state processing.

## APIs And Structures

- `ibcm_state_rc_trace_qualifier_t` enumerates trace event qualifiers for:
  - Initial displayed identifiers such as SID, channel, local/remote ComID, QPN, and timestamp.
  - Incoming CM MADs: REQ, REP, RTU, COMEST, MRA, REJ, LAP, APR, DREQ, DREP.
  - Outgoing CM MADs: REQ, REP, RTU, LAP, APR, MRA, REJ, DREQ, DREP.
  - IBMF send completions for corresponding messages.
  - REP timeout, client callback entry/return events, QP state transitions, error/set-alt transitions, stale detection, and retry events.
- `IBCM_MAX_CONN_TRCNT` defaults per-connection trace chunks to 40 events.
- `IBCM_DEBUG_BUF_SIZE` defines a 4096-byte debug buffer.
- `tm_diff_type` is `uint32_t`, with `TM_DIFF_MAX` as `UINT32_MAX`.
- `ibcm_conn_trace_t` stores base time, event array, event time deltas, current index, and allocated trace count.

## Functions And Globals

- `ibcm_insert_trace()` records a trace event for a connection state object.
- `ibcm_dump_conn_trace()` dumps the trace into `ibtf_debug_buf`.
- Extern globals include `ibcm_debug_buf`, trace mutexes, maximum trace count, trace enable flags, and `event_str[]`.

## Dependencies

- Referenced by `ibcm_state_data_t` in `ibcm_impl.h`.
- Uses kernel time (`hrtime_t`) and mutex primitives.

## Risks And Invariants

- Trace arrays are dynamically sized per connection and indexed by an 8-bit `conn_trace_ind`, so configured trace counts must fit intended indexing behavior.
- Timing deltas are limited to `uint32_t`; overflow needs to be tolerated or clamped by implementation.
- Trace control is global through `ibcm_enable_trace`, with separate mutexes for trace state and print serialization.

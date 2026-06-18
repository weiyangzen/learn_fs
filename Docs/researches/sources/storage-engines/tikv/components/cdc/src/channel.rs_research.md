# sources/storage-engines/tikv/components/cdc/src/channel.rs

## Purpose
Implements CDC event channels, memory accounting, batching into gRPC `ChangeDataEvent` responses, barrier handling, and drain cleanup.

## APIs, Types, And Functions
`CdcEvent` variants are `ResolvedTs`, `Event`, and `Barrier`. `CdcEvent::size` computes approximate or protobuf sizes. `EventBatcher` groups events under `CDC_RESP_MAX_BYTES`, keeps resolved-ts messages isolated, and tracks byte statistics. `channel` returns a `Sink`/`Drain` pair. `Sink::unbounded_send` sends observed events and `Sink::send_all` sends scanned events through a bounded channel with shared truncation flag. `Drain::drain` merges scanned and observed streams, frees truncated scanned events, records pending duration, and fires barriers. `Drain::forward` batches drained events into gRPC sink messages with buffered write flags.

## Control Flow
Observed events use an unbounded channel but are constrained by memory quota unless forced. Scanned events pre-allocate total quota, feed the bounded channel, and free quota on send failure. Draining selects between both streams, skips truncated scanned events, and returns `(event, size)`. Forwarding chunks up to 64 CDC events, builds one or more `ChangeDataEvent` responses, frees pending memory just before sending, feeds all responses with buffer hints, flushes the sink, records flush activity, and increments byte metrics.

## State And Persistence
State is in memory: futures channels, `MemoryQuota`, event timestamps, truncation flags, batching buffers, and connection ID. No persistent data is written. `Drop for Drain` closes receivers and synchronously drains remaining events to free memory quota, warning if this takes at least 200 ms.

## Dependencies And Integration Points
Depends on futures streams/sinks, grpcio `WriteFlags`, kvproto CDC protobufs, protobuf sizing, TiKV memory quota utilities, CDC metrics, connection IDs, and watchdog `FlushActivity`. It is the stream transport layer for CDC event-feed RPCs.

## Risks And Test Signals
Key risks are memory quota leaks, oversized response batching, resolved-ts ordering/isolation, barrier semantics, forced error-event sends bypassing quota, and blocking drain drop. Tests cover scanned truncation, barriers, nonblocking batching, congestion, capacity changes, force sends, memory leak scenarios, event batching layout/statistics, and resolved-ts size correctness. Failpoints can force event size or post-flush sleep.

# sources/storage-engines/foundationdb/fdbserver/worker/MetricClient.cpp

## Purpose
`MetricClient.cpp` implements `UDPMetricClient`, the process-local UDP emitter for FoundationDB metrics. It supports both OTLP msgpack emission and StatsD line emission depending on `FLOW_KNOBS->METRICS_DATA_MODEL`.

## Important APIs, Types, And Functions
The constructor chooses metric model, target address, and target port from knobs, allocates a reusable `MsgpackBuffer`, parses the destination address, and creates a UDP socket. `send_packet` wraps nonblocking `::send` on non-Windows platforms. `send(MetricCollection*)` serializes and emits metric sums, histograms, gauges, or StatsD messages.

## Control Flow
`send` returns early until the UDP socket future is ready and a native handle exists. For OTLP, it batches sums under a conservative packet-size cap, emits histograms one per packet, and emits gauges as a group, clearing each source map after emission. For StatsD, it concatenates newline-delimited messages up to `IUDPSocket::MAX_PACKET_SIZE` and sends the accumulated string.

## State And Persistence Behavior
The client has no durable state. It mutates the supplied `MetricCollection` by moving metric objects into temporary vectors and clearing maps/messages after attempted send. The reusable msgpack buffer is reset after packet emission.

## Dependencies And Integration Points
It depends on Flow network abstractions, UDP sockets, knobs, OTEL serialization helpers, TD metrics, Msgpack, trace events, and platform socket headers. It is driven by `runMetrics()` in `MetricLogger.actor.cpp`.

## Risks And Test Signals
Packet sizing and mutation semantics are the main risks. OTLP sums are moved out of maps before clear; histograms are sent individually because they can be large. The StatsD overflow branch currently calls `send_packet(socket_fd, buf.buffer.get(), buf.data_size)` instead of sending the accumulated `messages`, which is a potential bug if a packet fills before the final flush. Error handling records `errno` trace events for OTLP sends but does not retry or check return codes.

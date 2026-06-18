# sources/storage-engines/foundationdb/fdbclient/Tracing.cpp

## Purpose
`Tracing.cpp` implements concrete OpenTelemetry-style span tracing backends for fdbclient/Flow spans. It supports disabled tracing, trace-event logfile emission, and a lossy UDP MessagePack transport, with simulation validation for UDP serialization.

## Important APIs, types, and functions
`NoopTracer`, `LogfileTracer`, `UDPTracer`, and non-Windows `FastUDPTracer` implement `ITracer`. `openTracer()` switches the global tracer. `Span::~Span()` and move assignment emit sampled spans when a span lifetime ends. `simulationStartServer()` runs a UDP listener in simulation to validate packet shape. `fastTraceLogger()` periodically traces UDP sender counters. MessagePack helper methods serialize spans, linked contexts, events, and attributes.

## Control flow
When a sampled `Span` is destroyed or overwritten by move assignment, it records end time with `g_network->now()` and sends the span to `g_tracer`. Logfile tracing emits a primary `TracingSpan` event plus separate events for links, tags, events, and event attributes. UDP tracing serializes a 12-field array including trace ID, span ID, parent ID, location, begin/end, kind, status, links, events, and attributes. `FastUDPTracer::prepare()` lazily starts logging, creates a UDP socket, starts the simulation UDP server when needed, validates literal listener addresses, and records unready/send-failure counters. `write()` sends with `MSG_DONTWAIT` and disables further sends after an error.

## State and persistence behavior
Global `g_tracer` owns the active backend. `FastUDPTracer` maintains a reusable `MsgpackBuffer`, counters, socket future, socket fd, send-error flag, and background actors. Persistence is through trace logs or network-delivered UDP packets; no database keys are touched.

## Dependencies and integration points
The file depends on Flow MessagePack helpers, random/network/socket primitives, knobs, unit tests, UDP sockets, and span types from `Tracing.h`. It integrates with every subsystem that constructs `Span` objects and with trace log consumers or external UDP collectors.

## Risks and edge cases
UDP tracing is lossy by design. Hostnames are rejected because `NetworkAddress::parse()` expects literal IP addresses; invalid listener addresses disable sending with a warning. Serialization vector sizes above supported bounds assert or warn. The global tracer is replaced by `openTracer()` without synchronization visible here, so it should be configured in controlled phases. Move assignment emits the existing sampled span before stealing the new span's arena-backed fields, which is important for avoiding dangling references.

## Test signals
Local tests cover span sampling inheritance, adding events, attributes, links, and FastUDP MessagePack byte layout including long strings. Additional useful tests include invalid listener address handling, send-error backoff, simulation UDP server validation, tracer switching, and logfile field completeness.

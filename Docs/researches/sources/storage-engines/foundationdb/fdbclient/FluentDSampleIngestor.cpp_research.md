# sources/storage-engines/foundationdb/fdbclient/FluentDSampleIngestor.cpp

## Purpose
`FluentDSampleIngestor.cpp` implements the FluentD sink for actor-lineage profiler samples. It converts FoundationDB `NetworkAddress` values to Boost.Asio endpoints, serializes each `Sample` entry as a tiny MessagePack map keyed by wait-state name, and sends the records over TCP or UDP to a configured FluentD collector.

## Important APIs, Types, And Functions
The private helpers are `ipAddress()`, `toEndpoint()`, `FluentDSocket`, `SampleSender<Protocol, Callback>`, `makeSampleSender()`, and `FluentDSocketImpl<Protocol>`. The public-facing implementation is `FluentDIngestorImpl`, backing `FluentDIngestor::~FluentDIngestor()`, `FluentDIngestor::FluentDIngestor()`, `FluentDIngestor::ingest()`, and `FluentDIngestor::getConfig()`. `SampleSender` owns the per-sample send iterator and a retained `shared_ptr<Sample>`; `FluentDSocketImpl` owns socket state, a bounded pending-sample queue, and the failure code.

## Control Flow
Construction immediately chooses TCP or UDP and starts an async connect on `ActorLineageProfiler::instance().context()`. `ingest()` drops input while a retry timer is pending, schedules a reconnect after observing a socket failure, or passes the sample to the socket. If the socket is ready, the sample is serialized and sent immediately; otherwise it is queued up to `MAX_QUEUE_SIZE`. `SampleSender::sendNext()` walks all entries in `Sample::data`, computes a MessagePack buffer size, writes a single-entry map containing the wait-state string and pre-serialized value bytes, sends it synchronously through the Boost.Asio socket, and recurses via the completion handler until all entries are written.

## State And Persistence Behavior
All state is process-local. The ingestor stores the collector protocol, endpoint, socket pointer, retry timer, queue, readiness flag, and last `boost::system::error_code`. It does not persist data to FoundationDB. Backpressure is limited to an in-memory queue of 100 samples; extra samples are silently dropped. A failed socket is discarded and re-created after a one-second timer.

## Dependencies And Integration Points
This file depends on `fdbclient/ActorLineageProfiler.h`, `NetworkAddress`, `IPAddress`, `Sample`, Boost.Asio TCP/UDP sockets and timers, and MessagePack wire conventions. It integrates with the actor-lineage profiler as an optional telemetry exporter and reports configuration through `getConfig()`.

## Risks And Edge Cases
TCP writes use `socket.send()` once per buffer and do not loop for partial writes, so large buffers would rely on Boost.Asio's synchronous send semantics rather than explicit completion. UDP sends can fail if the endpoint was not connected or packets exceed datagram limits. MessagePack string encoding only handles fixstr and str8 lengths; wait-state names longer than 255 bytes would truncate the length byte. Failed sends only set `_failed`; callers see loss until the next `ingest()` notices and schedules retry. Queue overflow and connect/send errors have TODO trace comments rather than observability.

## Test Signals
No local `TEST_CASE` exists in this file. Useful signals are profiler integration tests that assert `getConfig()` output, TCP/UDP collector receipt of MessagePack maps, reconnect after collector restart, queue draining order, and sample drops/failures being visible in trace logs once TODOs are implemented.

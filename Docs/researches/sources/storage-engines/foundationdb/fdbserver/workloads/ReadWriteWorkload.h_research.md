## sources/storage-engines/foundationdb/fdbserver/workloads/ReadWriteWorkload.h

`ReadWriteWorkload.h` declares the metric descriptors and shared `ReadWriteCommon` base used by `ReadWrite.cpp`. It centralizes option parsing, metric state, key/value generation hooks from `KVWorkload`, setup/check/metrics declarations, and helper methods for latency logging and measurement-window filtering.

Important APIs and types are `KVWorkload`, `DDSketch`, `TDMetric` descriptors/handles, `PerfIntCounter`, `PerfMetric`, `boost::lexical_cast`, `Standalone<StringRef>`, and Flow futures. The descriptors define structured TD metrics for successful transactions (`totalLatency`, `startLatency`, `commitLatency`, `retries`), failed transactions (`startLatency`, `errorCode`), and individual reads (`readLatency`).

The constructor parses common options: duration, target TPS, allowed latency-derived actor count, reads/writes per A/B transaction, alpha, node-prefix key widening, measurement start/duration, edge-discard behavior, warming and insert throttles, debug trace windows, read latency logging, periodic interval, cancellation behavior, RYW mode, setup enablement, and insertion-count checkpoints. It also validates that `keyForIndex` remains monotonic for random key pairs.

State is mostly runtime metric state and workload configuration. Persistent behavior is delegated to `setup`, implemented in `ReadWrite.cpp` through `bulkSetup`; `operator()(uint64_t)` produces `KeyValueRef` pairs for bulk loading. Risks include the header's broad mutable public state, dependence on implementation in the `.cpp`, and option parsing that can silently ignore invalid insertion-count strings.

Integration points are concrete read/write workloads, bulk setup, Flow metric descriptors, and tester metric collection. Test signals are not emitted directly by the header, but it defines the counters, sketches, event metrics, and `shouldRecord` window used by the implementation.

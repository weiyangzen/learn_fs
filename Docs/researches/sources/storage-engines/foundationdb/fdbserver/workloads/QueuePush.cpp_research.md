## sources/storage-engines/foundationdb/fdbserver/workloads/QueuePush.cpp

`QueuePushWorkload` is a write-throughput workload that repeatedly finds one end of a synthetic key queue and inserts a new key beyond it. It can push forward from `0000000000000001` toward `9999999900000001` or backward from the end toward the start, measuring GRV and commit latency with `DDSketch`.

Important APIs are `Transaction`, `getReadVersion`, `getKey(lastLessThan/firstGreaterThan)`, snapshot reads, `PerfIntCounter`, `DDSketch`, and key formatting/parsing helpers. `keyForIndex(base, offset)` produces fixed 16-byte hex keys. `valuesForKey` parses the two 8-hex-digit components back into integers.

`start` launches `actorCount` write clients and times them out after `testDuration`. Each `writeClient` obtains a read version, snapshot-reads the current queue edge, defaults to the configured boundary if none exists, parses the edge key, and writes a new key whose base is adjusted by the parsed offset and whose offset is random in `[1,1000)`. It then commits, records commit latency, and increments transaction counters; retry loops call `tr.onError` and increment retries.

State persists generated queue keys and fixed-size random values in normal keyspace. Risks include hot contention on the queue edge, `valuesForKey` throwing if non-conforming keys appear near the selected boundaries, no setup clearing pre-existing keys, and possible integer movement beyond intended boundaries over long runs. Metrics divide by configured duration rather than observed runtime.

Integration points are key selector semantics, snapshot reads, commit path, and latency sketches. Test signals are throughput, bytes/sec, transaction/retry counts, and GRV/commit latency percentiles. `check` always returns true, so it is performance-oriented rather than correctness-validating.

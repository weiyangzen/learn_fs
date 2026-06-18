# sources/storage-engines/badger/badger/cmd/read_bench.go

Purpose: implements `badger benchmark read`, including random key reads and full-scan mode.

Important APIs and flow: flags configure goroutines, duration, sample size, keys-only mode, read-only open, full scan, and cache sizes. `readBench` opens Badger managed with cache settings, then either scans all entries with an iterator at `math.MaxUint64` or calls `readTest`. `getSampleKeys` uses a Badger stream to collect first-version keys into memory, stops via context cancellation when enough keys are sampled, then shuffles. Worker goroutines repeatedly call `lookupForKey`, which uses a key iterator and reads up to ten versions.

State and persistence: read-only by default, no DB mutations; global atomics track bytes and entries read. Dependencies are Badger streaming, iterators, protobuf, `z.Closer`, and random sampling. Risks: `keysOnly` flag is registered but not used by lookup logic, package-global counters are shared with write benchmarks, and empty DB handling is only in `readTest`. Test signals are benchmark throughput logs, full-scan counts, sampled-key counts, and cache-size sensitivity.

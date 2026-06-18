# sources/storage-engines/tikv/components/raftstore/src/store/worker/split_controller.rs

Purpose: this file implements load-based split decision logic. It collects sampled read key ranges, read/write flow, optional per-region CPU records, and thread CPU usage, then chooses split keys or hot key ranges for regions whose load repeatedly exceeds configured thresholds.

Important APIs and types:
- `sample` performs distributed reservoir-style sampling without replacement across multiple key-range providers.
- `Sample` and `Samples` evaluate candidate split keys by counting query ranges left, right, or containing the key, then choose the lowest combined balance/contained score that passes configured limits.
- `Recorder` stores per-region observations over `detect_times`, tracks peer, CPU usage, and hottest key range, and produces a split key when ready.
- `RegionInfo`, `ReadStats`, and `WriteStats` aggregate per-region query counts, sampled read ranges, flow statistics, bucket flow stats, and write query stats.
- `SplitInfo` represents either a concrete split key or a start/end range for half-splitting a hot CPU range.
- `AutoSplitController` owns recorders, tracked `SplitConfig`, thread-capacity settings, recent gRPC poll CPU samples, and optional unified read pool resize notifications.
- `AutoSplitControllerContext` batches incoming stats and periodically drops retained vectors/caches.

Control flow:
- Read-side callers build `ReadStats` by adding query key ranges or flow. Per-region `RegionInfo::add_key_ranges` performs reservoir sampling bounded by current `sample_num`.
- `AutoSplitController::flush` drains batched read stats and CPU stats, records gRPC and unified read pool thread usage, and computes whether gRPC poll/unified read pool are busy.
- For each region, flush skips disabled regions via `SplitValidator`, sums QPS/bytes, observes CPU usage if available, and discards recorders when QPS, bytes, and CPU conditions are all below threshold.
- Hot regions get a `Recorder`. The controller samples key ranges across threads, records them, and after `detect_times` observations tries to produce a balanced split key.
- If normal key selection fails but CPU conditions justify fallback, candidate region ids are saved. After the loop, the highest CPU candidate is split by its hottest key range only if gRPC poll is not busy.
- `refresh_and_check_cfg` consumes config tracker updates and signals whether the region CPU collector should be registered or unregistered when the CPU threshold crosses zero.

State and persistence behavior:
- All controller state is in-memory: recorders, recent gRPC usage, stat batches, CPU caches, and sampled ranges. No durable writes occur here.
- `ReadStats::region_buckets` can accumulate `BucketStat` flow deltas to be reported elsewhere; it updates bucket metadata when newer bucket meta arrives and merges retained flow.
- `AutoSplitControllerContext::maybe_gc` clears retained buffers and CPU caches every 30 seconds to bound memory retention under bursty load.

Dependencies and integration points:
- Uses `SplitConfigManager`/`SplitConfig` for runtime thresholds and `SplitValidator` to suppress regions temporarily.
- Consumes `resource_metering::RawRecords` for per-region CPU and hottest key-range inference.
- Uses `ThreadInfoStatistics` plus TiKV thread name prefixes to measure gRPC server and unified read pool CPU usage.
- Integrated from the PD worker stats monitor, which flushes stats, handles `SplitConfigChange`, and schedules resulting `SplitInfo` work.
- Emits metrics for load, sample quality, and split outcomes.

Risks and edge cases:
- Sampling is randomized and bounded by `DEFAULT_MAX_SAMPLE_LOOP_COUNT`; under pathological empty providers it can return fewer samples and only warn.
- Candidate key evaluation rejects keys that are too imbalanced or too often contained inside request ranges, avoiding splits that would increase cross-region RPC fanout.
- CPU fallback intentionally avoids splitting when gRPC poll is busy, because splitting can increase RPC load.
- `recorders` are time-bounded by `clear`, but stale recorders can otherwise hold sampled key ranges until flush/clear removes them.
- CPU usage calculation divides summed CPU time by collected duration; zero duration maps to zero usage.

Test signals:
- Tests cover prefix sums, sample position classification, recorder readiness and collection, raw/encoded/mixed key split selection, CPU fallback ranges, sample-size behavior with empty providers, reservoir bias expectations, config refresh transition events, CPU stat collection/hottest range selection, average gRPC CPU windowing, batch receive limits, and context GC. Benchmarks cover sample evaluation, flush, and query-stat recording.

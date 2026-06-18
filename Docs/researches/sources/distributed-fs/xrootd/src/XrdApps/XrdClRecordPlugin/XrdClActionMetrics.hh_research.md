<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdApps/XrdClRecordPlugin/XrdClActionMetrics.hh -->
# sources/distributed-fs/xrootd/src/XrdApps/XrdClRecordPlugin/XrdClActionMetrics.hh

Purpose: defines `XrdCl::ActionMetrics`, the replay-side accumulator for operation timing, byte counts, IOPS, errors, offsets, synchronicity, and human/json reporting.

Important APIs/types/functions: constructor seeds `delays` and `ios` maps for Open/OpenR/OpenW/Read/Write/Stat/Close/PgRead/PgWrite/Truncate/Sync/VectorRead/VectorWrite; `Dump(bool json)` renders per-file or summary metrics; getters aggregate read/write IOPS and bytes; `addDelays()` and `addIos()` are mutex-protected for async callbacks; `add()` combines another metric and tracks read/write synchronicity; `humanreadable()` formats byte counts; nested `synchronicity_t` averages read and write groups.

Control flow: replay initializes one metrics object per file and one summary. Action executors update counters before submission and update measured time/error counters from callbacks. After threads complete, metrics are optionally dumped individually, aggregated, and included in the final summary.

State/persistence: in-memory only. It stores maps keyed by string metric names and vectors of per-file synchronicity percentages for summary aggregation.

Dependencies/integration: integrates with `XrdClReplay.cc` callback paths, `Action` timing semantics, C++ mutexes, maps, vectors, and JSON/text output code.

Risks/test signals: JSON rendering manually removes the last comma by seeking backward, which can misbehave if no metrics were emitted for an object. Map key typos become user-facing metric names. Tests should cover empty metrics, json/text output with per-file and summary modes, async concurrent updates, read/write classification in `add()`, and human-readable byte thresholds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdApps/XrdClRecordPlugin/XrdClActionMetrics.hh -->

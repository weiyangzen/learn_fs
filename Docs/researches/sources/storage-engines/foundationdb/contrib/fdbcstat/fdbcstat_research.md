# sources/storage-engines/foundationdb/contrib/fdbcstat/fdbcstat

## Purpose
Linux BCC/eBPF utility that attaches uprobes to `libfdb_c.so` and reports FoundationDB C API call rate, average latency, and maximum latency per interval.

## Important APIs, Types, And Functions
Python configuration lists tracked functions: `get`, `get_range`, `get_read_version`, `set`, `clear`, `clear_range`, and `commit`, with `waitfuture` determining whether latency ends at API return or `fdb_future_block_until_ready`. The embedded BPF program defines `starttime`, `startfunc`, and `stats` hash maps plus entry probes and a shared return probe.

## Control Flow
The script parses PID, interval, duration, function filter, and library path. It resolves the library, specializes BPF text with an optional PID filter, compiles BPF, attaches entry uprobes to selected `fdb_transaction_*` symbols, attaches return probes either to transaction functions or `fdb_future_block_until_ready`, then sleeps by interval and aggregates BPF stats into terminal output.

## State And Persistence
Runtime state lives in eBPF maps and a Python aggregation dictionary cleared each interval. No files are written.

## Dependencies And Integration
Requires Linux, BCC Python bindings, kernel uprobe support, sufficient privileges, and a resolvable FoundationDB C client shared library. It observes external FoundationDB client processes.

## Risks
The aggregation path compares `v.cnt > agg[f]['max']` instead of `v.max > agg[f]['max']`, likely underreporting or corrupting max latency updates. Wait-future attribution uses per-thread start maps, so nested/overlapping futures on the same thread can overwrite state. Symbol names may not match all ABI-versioned aliases. Typographical comments do not affect runtime but indicate limited polish. Requires privileges and can fail silently if uprobes do not match.

## Test Signals
Run against a small client issuing known operations, compare counts with client-side instrumentation, test function filters, PID filter, no matching symbols, wait-future operations, and max latency aggregation.

# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdFileStats.hh

Purpose: defines per-file monitoring counters for transfer bytes, operation counts, page read/write activity, and optional sum-of-squares statistics used by xrootd monitoring.

Important APIs and types: fields include `FileID`, monitor table entry, monitor level, transfer-executed flag, opened file size, `XrdXrootdMonStatXFR`, `OPS`, and `PRW` structs, plus `ssq` accumulators. `Init()` resets all fields and establishes minimum sentinel values. Inline update methods include `pgrOps()`, `pgwOps()`, `pgUpdt()`, `rdOps()`, `rvOps()`, `wrOps()`, and `wvOps()`.

Control flow and state: updates are gated by `monLvl`; deeper stats are collected only at higher levels (`monOps`, `monSsq`). Normal reads/writes update byte counters, operation counts, min/max sizes, and optional sum-of-squares. Page read/write counters are accumulated separately and later folded into normal counters on file close by `XrdXrootdFileTable::Del()`.

Dependencies and integration: includes `XrdXrootdMonData.hh`, and is embedded directly in `XrdXrootdFile`. Monitoring close paths pass these counters to `XrdXrootdMonitor` and `XrdXrootdMonFile`.

Risks and test signals: counters are inline and likely updated from request paths, so thread safety depends on surrounding file/request serialization. Tests should validate min/max initialization, level-gated updates, page retry/error accounting, writev treatment as write, and close-time aggregation of page stats.

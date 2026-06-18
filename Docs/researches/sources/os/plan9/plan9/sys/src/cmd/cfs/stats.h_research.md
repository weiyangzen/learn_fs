# File Research: sources/os/plan9/plan9/sys/src/cmd/cfs/stats.h

Defines CFS statistics data structures. `Cfsmsg` tracks per-message count, accumulated time, and last-call start time. `Cfsstat` keeps 128 client and 128 server message buckets plus cache, directory-read, and byte-flow counters. Exports global current/previous stats (`cfsstat`, `cfsprev`) and `statson` toggle.

Key role: shared instrumentation schema for the Plan 9 cache filesystem command, not behavior itself.

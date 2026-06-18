# File Research: sources/os/bsd/openbsd-src/sys/sys/smr.h

Safe memory reclamation primitives and SMR-aware list macros.

This header defines `struct smr_entry` callback records, SMR startup/read-side/callback/barrier APIs, and pointer access macros using `READ_ONCE`, `WRITE_ONCE`, and producer barriers. Diagnostic builds assert whether the current CPU is inside or outside an SMR critical section.

Most of the file adapts queue-style containers for lock-free SMR readers: `SMR_SLIST_*`, `SMR_LIST_*`, and `SMR_TAILQ_*`. Reader traversal uses SMR pointer reads, while mutation macros are explicitly `_LOCKED` and preserve removed elements' forward links so concurrent readers can finish iteration safely.

Filesystem/storage relevance: SMR is a generic kernel concurrency primitive. It matters to filesystem and VFS code when shared lookup tables, caches, or object lists need lockless readers with deferred reclamation.

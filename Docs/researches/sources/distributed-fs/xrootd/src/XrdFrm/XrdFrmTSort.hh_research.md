## sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmTSort.hh

Purpose: declares the purge candidate sorter. It is specialized for `XrdFrmFileset` objects and access-time aging, not a general container.

Important APIs/types: `Add()` transfers a fileset into the sorter, `Oldest()` removes and returns the next purge candidate, `Count()` reports the number of entries, and `Purge()` deletes all queued entries. Constants define four six-bit time tiers: seconds, minutes, hours, and days. `sortSZ` controls whether final-bin insertion sorts by file size.

State and persistence: runtime-only arrays and counters track bucket heads and high-water indices. The class owns queued fileset pointers.

Dependencies and integration: forward declares `XrdFrmFileset`, so consumers can include the header without scanner internals. `XrdFrmPurge` embeds one sorter per space policy.

Risks and test signals: copy/assignment are not disabled despite pointer ownership; accidental copying would double-delete. Tests or static analysis should flag copying, and unit tests should cover destructor cleanup.

# sources/sync-backup/syncthing/lib/ur/memsize_unimpl.go

Purpose: fallback memory-size implementation for unsupported platforms.

Important APIs and control flow: build tags select this for platforms other than Darwin, Linux, NetBSD, Solaris, and Windows. `memorySize` returns zero.

State and persistence: none.

Dependencies and integration: allows usage reporting to compile on all supported platforms while omitting physical memory size where not implemented.

Risks and signals: reports from these platforms lack memory-size data. No tests needed.

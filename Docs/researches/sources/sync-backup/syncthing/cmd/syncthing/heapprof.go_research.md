# sources/sync-backup/syncthing/cmd/syncthing/heapprof.go

Purpose: optional debug heap profiler for the Syncthing process.

Important APIs/functions: `startHeapProfiler` and `saveHeapProfiles`.

Control flow: `startHeapProfiler` starts a goroutine and panics if profile saving fails. `saveHeapProfiles` sets `runtime.MemProfileRate`, periodically reads memory stats, and when `HeapInuse` increases writes a heap profile to `heap-<pid>.pprof.tmp`, closes it, removes the old target, and renames atomically.

State and persistence: writes one rolling heap profile file in the working directory and mutates runtime memory profiling rate.

Dependencies/integration: enabled by `serveCmd.syncthingMain` debug flags/env.

Risks and test signals: high-frequency polling and low profile rate can affect performance. Errors abort via panic. No tests cover profiler file lifecycle.

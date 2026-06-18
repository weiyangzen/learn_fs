# sources/storage-engines/foundationdb/fdbrpc/AsyncFileChaos.h

Purpose: simulation wrapper around `IAsyncFile` that injects disk delays and write corruption for storage files. It is used to exercise storage robustness under simulator-controlled disk failures.

Important APIs and type: `AsyncFileChaos` implements `IAsyncFile` and reference counting. Methods wrap `read`, `write`, `truncate`, `sync`, `size`, `debugFD`, and `getFilename`. `getDelay` consults `DiskFailureInjector` and updates `ChaosMetrics`.

Control flow: constructor enables chaos only for filenames containing `storage-` and excluding `sqlite-wal`. Reads, truncates, syncs, and size calls delay before forwarding when the injector returns a delay. Writes may copy the buffer into an arena, flip a random bit according to `BitFlipper`, log the corrupted block, update metrics, delay, then write either corrupted or original data.

State and persistence behavior: wrapper has no durable state, but injected corruption is persisted by forwarding corrupted bytes to the underlying file. In simulation, corrupted block metadata is tracked in `g_simulator->corruptedBlocks` and pruned on truncate.

Dependencies and integration points: depends on Flow futures, simulator globals, `DiskFailureInjector`, `BitFlipper`, `ChaosMetrics`, deterministic random, and `IAsyncFile`.

Risks: `truncate` accesses `g_simulator->corruptedBlocks` in the delayed path without checking simulation mode, assuming this wrapper is used in simulator contexts. `getClassName` returns `"AsyncFileReadAheadCache"`, which appears copied and may be misleading for diagnostics.

Test signals: no direct unit tests here; simulator workloads and chaos metrics provide integration coverage.

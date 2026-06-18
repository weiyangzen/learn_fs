# sources/test-tools/syzkaller/pkg/manager/repro.go

Purpose: Defines manager crash/repro data structures and the generic reproduction scheduler used by normal manager mode and patch-diff mode.

Important APIs and types: `ReproResult` captures the original crash, syz repro, strace result, stats, and error. `Crash` wraps `report.Report` with source flags, manual/full repro flags, ext request id, tail reports, and memory dump path. `Crash.FullTitle` creates a stable scheduling key. `ReproManagerView` abstracts manager callbacks. `ReproLoop` owns queue, running set, attempt counts, VM slot channel, and stats.

Control flow: `NewReproLoop` initializes stats and capacity. `Enqueue` records dedupe in `onlyOnce` mode, appends a crash, and pings the loop. `popCrash` selects the best runnable crash: full repros first, fewer attempts first, manual before automatic, non-hub before hub, and never same title while already reproducing. `Loop` seeds reproduction slots based on `calculateReproVMs`, repeatedly selects needed crashes, waits for a slot, marks them reproducing, adjusts reserved VM count, and runs `handle` in a goroutine. On completion it clears state, releases slot, and pings the queue. `adjustPoolSizeLocked` reserves roughly 1.33 VMs per unique active/pending title.

State and persistence: All scheduling state is in memory under `mu`. Persistence of repro artifacts is delegated to the concrete manager’s `RunRepro` path.

Dependencies and integration: Used by `diffContext`, HTTP dashboard (`Reproducing`, `Empty`, `CanReproMore`), manager crash handling, `report`, `repro`, and `stat`.

Risks: `CanReproMore` reads channel length without lock and is advisory only. Queue priority is O(n). A manager callback that blocks indefinitely consumes slots until context cancellation. Same-title serialization prevents redundant work but can delay independent crashes with identical titles.

Test signals: `repro_test.go` covers scheduling capacity, order, dedupe race with `NeedRepro`, cancellation, and skipping unneeded queued crashes.

# Research: sources/sync-backup/syncthing/test/parallel_scan_test.go

## sources/sync-backup/syncthing/test/parallel_scan_test.go

Purpose: stress test for concurrent immediate rescans.

Important APIs/functions: `TestRescanInParallel`, `st.Rescan("default")`, and `sync.WaitGroup.Go`.

Control flow: cleans h1 state, generates 5000 files, writes `.stignore`, starts h1, launches 20 concurrent rescan requests, waits for all to finish, sleeps two seconds, and stops with log checking.

State and persistence: data under `s1`, h1 index, `.stignore`.

Dependencies and integration: scanner concurrency, REST rescan endpoint, test helper `checkedStop`. Risks include Go version dependency for `WaitGroup.Go`, race detector/log failure exposure, and long runtime with large file count. Test signal is no rescan errors and clean shutdown.

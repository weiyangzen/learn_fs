# Research: sources/sync-backup/syncthing/test/delay_scan_test.go

## sources/sync-backup/syncthing/test/delay_scan_test.go

Purpose: integration stress test for concurrent delayed rescan requests.

Important APIs/functions: `TestRescanWithDelay` and `st.RescanDelay("default", 1)` invoked from 20 goroutines.

Control flow: cleans `s1` and h1 indexes, generates 50 files, writes `.stignore`, starts instance 1, launches parallel delayed rescans, waits for all to return, sleeps briefly, and stops the instance. The stop helper checks logs for races/errors.

State and persistence: data under `s1`, `.stignore`, h1 database files.

Dependencies and integration: Syncthing REST/control API via integration helpers, concurrent Go test execution, filesystem scanning internals. Risks include data-race exposure, request coalescing regressions, and delayed scan scheduling bugs. Test signal is absence of errors/race output rather than a final directory comparison.

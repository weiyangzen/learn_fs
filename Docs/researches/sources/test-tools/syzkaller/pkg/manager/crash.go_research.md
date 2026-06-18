## sources/test-tools/syzkaller/pkg/manager/crash.go

Purpose: persists, indexes, and reports syz-manager crashes and reproducers under the manager workdir.

Important APIs/types/functions: `CrashStore`, constants `reproFileName`, `cReproFileName`, `straceFileName`, `MaxReproAttempts`, constructors `NewCrashStore`/`ReadCrashStore`, `SaveCrash`, `HasRepro`, `MoreReproAttempts`, `SaveFailedRepro`, `SaveRepro`, `Report`, `BugInfo`, `getSubsystems`, `querySubsystems`, `BugList`, `crashHash`, `path`, and `HasMemoryDump`.

Control flow: crash titles hash to `workdir/crashes/<hash>`. `SaveCrash` writes description, rotates bounded log/report/tag/machineInfo slots by oldest mtime, updates title stats, and moves memory dump. Repro saving writes syz/C repros, report/log, assets as gzip, strace data, and stats. `BugInfo` reads crash directory metadata, reports repro status/attempts/crashes/memory dump, computes impact rank and subsystem labels. `BugList` lists valid crash dirs sorted by title.

State and persistence: durable crash directory tree under workdir, including description, logs, reports, repro files, assets, strace, stats, title stats, and vmcore. Subsystem lookups are cached in memory behind a mutex.

Dependencies and integration: integrates manager config, `report`, `subsystem.Extractor`, `prog` assets, `osutil`, `hash`, and repro result types from manager package.

Risks: many file writes intentionally ignore errors after the initial description, so partial repro records are possible. Crash hash is title-only, grouping same-title crashes. Moving memory dump consumes the temp file path. Subsystem extraction depends on available repro/report data and reporter heuristics.

Test signals: manager `crash_test.go` outside this work item covers crash list, max logs, repro, memory dump, and subsystem behavior.

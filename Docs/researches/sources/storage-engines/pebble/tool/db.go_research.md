## sources/storage-engines/pebble/tool/db.go

Purpose: implements the `pebble tool db` command family for opening DBs, inspecting state, running consistency checks, mutating simple keys, estimating space, checkpointing, upgrading, excising ranges, printing metrics/properties, and delegating analyze/IO subcommands. `dbT` is both command registry and shared state holder.

Important APIs/types/functions: `dbT` owns Cobra commands, Pebble options, comparer/merger registries, formatting flags, remote/excise hooks, and analyze/benchmark flags. `newDB` constructs commands and flags. `initOptions` and `loadOptions` parse OPTIONS files, resolving custom comparer/merger/key schema hooks. `OpenOption` plus `nonReadOnly` alter options before `pebble.Open`. Command handlers include `runCheck`, `runUpgrade`, `runCheckpoint`, `runGet`, `runLSM`, `runScan`, `runSpace`, `runExcise`, `runProperties`, `runSet`, `inspectManifest`, and `readCurrentVersion`. `props`, `propArgs`, `addProps`, and `makePlural` support property aggregation.

Control flow: most commands initialize options, open the DB read-only by default, perform one operation, print errors to Cobra stderr, and close through `closeDB`. Mutating commands pass `nonReadOnly` and may require `promptForConfirmation`. `runExcise` builds a temporary SST with point and range-key excise tombstones inside the DB directory, ingests it through `IngestAndExcise`, and removes the temp file. `runProperties` avoids opening the DB; it peeks the manifest, replays the current version, opens table backings through an object provider, and aggregates property blocks per level plus total.

State and persistence: OPTIONS parsing mutates `d.opts` comparer, merger, key schema, and schema map. `openDBInternal` clones options, nulls explicit cache in favor of `CacheSize`, and clears unregistered key schema names. Mutating commands persist DB changes, format upgrades, checkpoints, or excise tombstones. `readCurrentVersion` replays MANIFEST into a `manifest.Version` and updates key/value formatters when the manifest declares a comparer.

Dependencies and integration: integrates Pebble DB APIs, `manifest`, `record`, `sstable`, `objstorageprovider`, `logs.NewCmd`, and analyze/benchmark implementations in sibling files. It is the main command tree consumed by `tool.New` and datadriven tests.

Risks: shared flag fields on `dbT` are command-global, so repeated command execution in one process relies on Cobra parsing order and test isolation. `runExcise` disables background behaviors on a local `dbOpts` pointer but opens through `d.openDB`, so future option plumbing changes could undermine assumptions. Virtual SSTs are skipped in `runProperties`. `runGet` prints Pebble errors such as not found on stderr rather than a structured status.

Test signals: `TestDB` datadriven suites cover command output. `data_test.go` stabilizes time and metrics. Analyze and LSM tests cover handlers implemented in sibling files.

# sources/sync-backup/syncthing/lib/model/model_test.go

## Purpose

`model_test.go` is the broad regression and behavior suite for Syncthing's model service. It builds fake configurations, fake filesystems, fake protocol connections, and DB state to validate how `model.go` handles protocol requests, folder lifecycle, config changes, cluster config exchange, auto-accept, introducers, ignore files, scanning, connection cleanup, request limits, completion accounting, encryption compatibility, pending offers, and rename/block metadata.

The tests double as executable documentation for model edge cases. Many test names reference historical Syncthing issues, indicating bug-regression protection around deadlocks, panics, DB accounting, stale connection state, and scan consistency.

## Important APIs, Helpers, and Test Groups

- `newState` wraps config, starts a test model, and adds fake device connections.
- `createClusterConfig` and `addFolderDevicesToClusterConfig` build BEP cluster configs with local and remote device entries.
- `genFiles` creates deterministic `protocol.FileInfo` slices for index and benchmark scenarios.
- `saveConfig` and `loadConfig` are test-local copies for checking remote device name persistence.
- `changeIgnores` validates `LoadIgnores` and `SetIgnores` round trips.
- `waitForState` observes `events.StateChanged` until a folder reports an expected error string.
- `testConfigChangeTriggersClusterConfigs` asserts which connected devices receive cluster configs after folder sharing changes.
- `modtimeTruncatingFS` and `modtimeTruncatingFileInfo` simulate filesystems with coarse modtime resolution.
- `countIterator` consumes iterator/error-function pairs and fails tests on iterator errors.

Major test groups cover:

- Request security and semantics (`TestRequest`, request benchmarks, `TestRequestLimit`, `TestNewLimitedRequestResponse`).
- Cluster config, encryption, auto-accept, and introducer behavior (`TestClusterConfig`, `TestClusterConfigEncrypted`, `TestIntroducer`, many `TestAutoAccept...`, `TestCcCheckEncryption`, `TestCCFolderNotRunning`).
- Folder lifecycle and config commits (`TestIssue4357`, `TestPausedFolders`, `TestFolderRestartZombies`, cluster-config resend tests).
- Ignore file behavior (`TestIgnores`, `TestEmptyIgnores`, `TestIssue4094`, `TestIssue4903`).
- Scanning and DB accounting (`TestROScanRecovery`, `TestRWScanRecovery`, `TestInternalScan`, rename tests, block-list map tests, receive-only deletion tests).
- Connection and device cleanup (`TestDeviceRename`, `TestSharedWithClearedOnDisconnect`, `TestConnCloseOnRestart`, `TestDevicePause`, `TestDeviceWasSeen`).
- API-facing views (`TestGlobalDirectoryTree`, `TestFolderAPIErrors`, `TestSummaryPausedNoError`, completion tests, pending folder tests).

## Control Flow

Most tests construct a config wrapper, create a model using helper constructors, optionally start the model supervisor, mutate fake filesystem state or protocol state, then call model methods synchronously. For protocol flows, fake connections are added with `AddConnection`, cluster configs are injected with `ClusterConfig`, indexes with `Index`/`IndexUpdate`, and outbound cluster config delivery is observed through fake connection call hooks.

Auto-accept tests simulate remote devices announcing folders under many combinations: new folder, existing folder, multiple devices, disabled auto-accept, label/ID path selection, path conflicts, paused local folders, encrypted and unencrypted announcements, and concurrent acceptance. The tests then inspect `m.cfg.Folder` and sharing lists to confirm config mutation outcomes.

Scan tests mutate fake filesystems, call `ScanFolder` or `ScanFolders`, then inspect DB-derived APIs such as `LocalSize`, `GlobalSize`, `ReceiveOnlySize`, `LocalFilesSequenced`, `CurrentFolderFile`, and `AllForBlocksHash`. Several tests use timeouts because pull/index side effects are asynchronous.

Connection tests add fake or protocol connections, trigger config changes that pause/remove devices or folders, and wait for close channels, event subscriptions, or fake connection calls. These flows verify the model does not hold locks across blocking close/start paths.

## State and Persistence Behavior

The suite validates both in-memory maps and persistent DB/config effects. It checks that remote device names can be stored into config, pending folders are inserted/filtered/removed from `ObservedDB`, folder removal drops pending associations, unknown remote indexes are dropped when a folder starts, removed devices are removed from config and model connection/download/hello maps, and request limiters release semaphore capacity after responses close.

Filesystem persistence is exercised through fake and basic filesystems. Ignore tests assert empty ignore content deletes `.stignore`, non-empty content writes it, paused folder paths can be created for ignore writes, and missing fake paths are treated as empty ignore sets. Encryption tests cover token computation and cached token behavior but skip expensive token generation in short mode.

DB state is checked for rename sequence adjacency, block-hash lookup update after remove/modify/rename/type-change operations, deleted file accounting, receive-only changed flags, completion counters, and index reset metadata.

## Dependencies and Integration Points

Tests depend on Syncthing's internal test helpers, fake filesystem implementations, fake protocol connections, mock connection info, event logger subscriptions, config wrappers, `db` counts/observed records, protocol vectors and file info structs, versioner constants, scanner side effects through `ScanFolder`, and semaphore behavior.

Benchmarks integrate with the same model setup to measure full index, incremental index, outbound request, inbound request, and directory tree generation costs at different scales.

## Risks and Edge Cases Captured

- Security-sensitive request handling rejects invalid paths, unshared folders, negative sizes, nonexistent files, missing or mismatched hashes, and read-past-EOF unless the short read hash matches.
- Auto-accept historically risked panics or path corruption around paused folders and concurrent config commits.
- Introducer removals must not remove devices shared independently or when removal skipping is configured.
- Folder restarts must be serialized to prevent duplicate runners.
- Request limiters must block concurrent oversized requests and release capacity on response close.
- Connection close during restart must not deadlock when protocol readers block.
- Scan logic must not mark inaccessible directory contents deleted, must handle directory/file type changes, case-only renames, batch flushes, and deleted receive-only states correctly.
- Cluster config generation for folders not fully running must still include expected folder/device metadata without exposing invalid index data.

## Test Signals

The file is itself the primary test signal for `model.go`. It contains dozens of unit/regression tests and several benchmarks. The coverage is strongest around externally observable behavior and historical regressions. Lower-level helper functions in `model.go` are commonly tested through model-level flows rather than isolated unit tests, which is appropriate for this integration-heavy component but means failures can sometimes require tracing through config, DB, protocol, and folder runner helpers.

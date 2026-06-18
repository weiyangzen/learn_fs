# sources/sync-backup/kopia/snapshot/upload/upload_actions.go

## Purpose
Implements before/after snapshot and folder action execution for uploads. Actions let policy-defined commands or scripts run around source directories and optionally redirect the snapshot source path.

## Important APIs, Types, and Functions
`actionContext` carries `ActionsEnabled`, random `SnapshotID`, source/snapshot paths, and temporary `WorkDir`. `ensureInitialized` lazily creates the context. `envars` produces `KOPIA_ACTION`, `KOPIA_SNAPSHOT_ID`, `KOPIA_SOURCE_PATH`, `KOPIA_SNAPSHOT_PATH`, and `KOPIA_VERSION`. `prepareCommandForAction` converts a `policy.ActionCommand` into `exec.Cmd`. `runActionCommand` executes sync, async, or essential actions and captures stdout key/value output. `executeBeforeFolderAction`, `executeAfterFolderAction`, and `cleanupActionContext` are called by the uploader.

## Control Flow
A before action initializes context only for local paths and only when uploader actions are enabled. Script actions are materialized into the temporary work directory with `.sh` or `.cmd`; command actions use the configured binary and arguments. Sync actions collect stdout and parse requested captures. Essential action failures abort the before action; non-essential failures are logged. If before action emits `KOPIA_SNAPSHOT_PATH`, the uploader opens that local directory and snapshots it instead. After actions log failures but do not change upload results.

## State and Persistence Behavior
State is transient: a temporary working directory and any action subprocess side effects. The only uploader-visible state carried across before/after hooks is `actionContext`, especially snapshot ID and potentially overridden snapshot path. Cleanup removes the temp directory.

## Dependencies and Integration Points
Depends on `policy.ActionCommand`, `localfs.Directory`, `repo.BuildVersion`, OS runtime detection, and uploader logging. Called from root and nested directory upload paths in `upload.go`.

## Risks
Actions execute user-provided scripts/commands and inherit the process environment plus Kopia variables. Async mode starts without waiting, so cleanup of the work directory can race with long-running scripts. Captures use simple `key=value` parsing and ignore unknown keys. After-action errors are intentionally non-fatal, which can hide cleanup failures.

## Test Signals
Direct tests are not in this subset, but upload tests exercise action-enabled repository setup and OS snapshot disabling. Useful tests would cover script/command modes, timeout, essential versus non-essential failures, path override, Windows extension behavior, capture parsing, and temp cleanup.

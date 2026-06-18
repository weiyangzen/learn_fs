
# sources/sync-backup/kopia/tests/end_to_end_test/snapshot_actions_test.go

## Purpose
Tests snapshot action hooks configured through policies: before/after snapshot root actions, before/after folder actions, embedded/persisted scripts, action enablement controls, async/optional/essential modes, timeout behavior, stdout-driven source redirection, environment variables, and ignore-rule handling after action redirection.

## Important APIs, Types, And Functions
- `TestSnapshotActionsBeforeSnapshotRoot` validates action failure stops snapshots in essential mode, optional/async modes do not, timeout kills long-running hooks, and `KOPIA_SNAPSHOT_PATH` redirection is honored only for synchronous hooks.
- `TestSnapshotActionsBeforeAfterFolder` configures per-folder before/after actions and checks inheritance boundaries and action environment values.
- `TestSnapshotActionsEmbeddedScript` uses `--persist-action-script` and validates successful scripts, failing scripts, and redirect scripts.
- `TestSnapshotActionsEnable` tests repository-level `--enable-actions` / `--no-enable-actions` and snapshot-level `--force-enable-actions` / `--force-disable-actions` precedence.
- `TestSnapshotActionsHonorIgnoreRules` verifies `.kopiaignore` is applied in the redirected snapshot directory.
- Helpers include `tmpfileWithContents`, `verifyFileExists`, `mustReadEnvFile`, and `skipUnlessTestAction`.

## Control Flow
Tests require `TESTING_ACTION_EXE`, create a repository with or without action support, set policy action commands, run `snapshot create`, then inspect marker files, env dump files, snapshot object IDs, and listed entries. Hook behavior is driven through a test action executable that can save env, create files, sleep, exit with a code, or emit stdout.

## State And Persistence Behavior
Policies persist action command configuration and command mode/timeouts. Actions mutate filesystem marker/env files and can redirect snapshot source paths through stdout. Snapshot manifests prove whether redirection occurred by comparing root object IDs against known source snapshots.

## Dependencies And Integration Points
Uses `policy set`, `snapshot create`, `snapshot list`, `ls`, `testenv`, `clitestutil`, `snapshot.Manifest`, and the external `TESTING_ACTION_EXE`. Integrates policy inheritance, command execution, environment propagation, snapshot source selection, and ignore rules.

## Risks And Edge Cases
Tests are skipped if the action executable is missing. Async behavior is timing-sensitive and uses elapsed time checks. Windows embedded scripts use different syntax from Unix scripts. Several marker variable names intentionally reuse paths, so diagnosing failures requires reading action env/marker assertions carefully. Hook stdout parsing is a security-sensitive path because it can redirect snapshot roots.

## Test Signals
Strong signal for action policy execution, source-redirection semantics, action enablement precedence, and action environment compatibility.

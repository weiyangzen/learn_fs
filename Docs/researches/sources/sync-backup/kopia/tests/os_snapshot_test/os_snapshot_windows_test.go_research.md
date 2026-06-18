
# sources/sync-backup/kopia/tests/os_snapshot_test/os_snapshot_windows_test.go

## Purpose
Tests Windows Volume Shadow Copy behavior for locked files when Kopia policy enables volume shadow copy.

## Important APIs, Types, And Functions
- `TestShadowCopy` requires `KOPIA_EXE`, creates a filesystem repo, enables `--enable-volume-shadow-copy=when-available`, creates an auto-delete locked file, checks admin/VSS permission, then expects snapshot success as admin or failure as non-admin.
- `createAutoDelete` uses Windows `CreateFile` with `FILE_FLAG_DELETE_ON_CLOSE` and no sharing to create a locked file.

## Control Flow
The test uses the external Kopia binary runner, writes and syncs a locked file, calls `vss.Get` to infer administrative access, snapshots the directory, lists snapshots and root entries, and validates content visibility depending on admin status.

## State And Persistence Behavior
Persists a temporary filesystem repository and a snapshot manifest. The locked file is deleted on close through Windows file-handle semantics.

## Dependencies And Integration Points
Uses `github.com/mxk/go-vss`, `golang.org/x/sys/windows`, `syscall`, `testenv.NewExeRunnerWithBinary`, `clitestutil`, and `KOPIA_EXE`.

## Risks And Edge Cases
Windows-only and depends on admin privileges and VSS availability. Non-admin expectations still require a snapshot/source listing path to exist. Locked-file behavior is specific to Windows handle flags.

## Test Signals
Important platform signal for VSS integration and fallback behavior around inaccessible files.

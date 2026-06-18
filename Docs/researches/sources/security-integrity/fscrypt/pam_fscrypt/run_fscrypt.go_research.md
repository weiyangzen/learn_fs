# sources/security-integrity/fscrypt/pam_fscrypt/run_fscrypt.go

## Purpose
`run_fscrypt.go` contains support code for executing PAM module functions: argument parsing, syslog setup, panic handling, system-user skipping, login protector discovery, policy scanning, and session count tracking.

## Important APIs, Types, and Functions
`PamFunc` wraps a named PAM operation. Important functions include `isSystemUser`, `(*PamFunc).Run`, `parseArgs`, `setupLogging`, `loginProtector`, `policiesUsingProtector`, `AdjustCount`, and `getCount`. Constants define `/run/fscrypt` count files, permissions, count format, and `uidMin`.

## Control Flow
`Run` parses argv, configures logging, defers panic-to-syslog conversion, creates a PAM handle, skips users below `uidMin` except root, and invokes the wrapped implementation. `loginProtector` builds an actions context for the login protector mountpoint, applies trusted-user restrictions unless cross-user metadata is allowed, then selects a PAM passphrase protector matching the PAM UID. `policiesUsingProtector` scans all filesystems, follows protectors, lists policies, loads each policy in a cloned context, filters by protector usage and provisioned state, and returns matches. `AdjustCount` creates `/run/fscrypt`, locks a per-UID count file, clamps counts at zero, rewrites the count, and returns it.

## State and Persistence
Session counts are persisted in tmpfs under `/run/fscrypt/<uid>.count` with root-only permissions and reset on reboot. Logging goes to syslog. Policy scans read metadata across mounted filesystems but do not directly modify it.

## Dependencies and Integration Points
Depends on `actions`, `filesystem.AllFilesystems`, `metadata`, PAM handles, `util.PointerSlice`, and `unix.Flock`. It supports all exported hooks in `pam_fscrypt.go`.

## Risks
Count files need root privileges and correct locking; stale counts can affect whether close-session locks policies. Policy scanning can be expensive across many filesystems and is sensitive to metadata ownership rules. Panic handling converts failures to PAM service errors but cannot undo partial provisioning.

## Test Signals
`run_test.go` only verifies empty argument parsing. Most behavior needs integration tests with PAM handles, metadata, mounted filesystems, and syslog.

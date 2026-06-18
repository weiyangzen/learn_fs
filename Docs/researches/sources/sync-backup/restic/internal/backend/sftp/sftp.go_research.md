<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/sftp/sftp.go -->
# sources/sync-backup/restic/internal/backend/sftp/sftp.go

## Purpose
Implements the SFTP backend over an ssh/sftp subprocess.

## Important APIs, Types, And Functions
SFTP, NewFactory, startClient, Open/Create/open, mkdirAllDataSubdirs/mkdirAll, buildSSHCommand, Save, Load/openReader, Stat, Remove, List, Close, Delete, Warmup/WarmupWait, and helper functions are central.

## Control Flow
startClient builds an ssh command, starts it, wires stdin/stdout to pkg/sftp, and detects posix-rename support. Create creates layout directories concurrently. Save writes a unique temp file, chmods, uses concurrent upload, validates length, closes, renames, then makes read-only. Load delegates to util.DefaultLoad and can detect too-short limited reads under BackendErrorRedesign. List walks the remote tree respecting layout subdir mode.

## State And Persistence Behavior
Repository state is remote filesystem data under DefaultLayout. Local state includes sftp client, subprocess, result channel, config, modes, and posixRename capability.

## Dependencies And Integration Points
Depends on pkg/sftp, os/exec, terminal, errgroup, backend/layout/limiter/location/util, feature flags, backoff, crypto/rand.

## Risks And Edge Cases
Risks include subprocess lifecycle, remote permission/mode support, non-atomic rename without posix extension, no-space detection via statvfs heuristics, and partial temp cleanup.

## Test Signals
sftp_test.go, sshcmd_test.go, layout tests, and generic suite cover command building, permissions, layout, and backend contract behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/sftp/sftp.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/sftp/sftp_test.go -->
# sources/sync-backup/restic/internal/backend/sftp/sftp_test.go

## Purpose
Runs SFTP backend suite and permission-specific tests against an available sftp-server binary.

## Important APIs, Types, And Functions
findSFTPServerBinary, testConfig, newTestSuite, TestBackendSFTP, BenchmarkBackendSFTP, TestCreateSetsDirPermissions, and TestSaveSetsDirPermissions are key.

## Control Flow
Tests locate sftp-server, create temporary repos, run shared suite/benchmarks, and assert directory modes after Create and Save-created subdirectories.

## State And Persistence Behavior
Uses external subprocess and temporary filesystem state.

## Dependencies And Integration Points
Depends on backend/test Suite, sftp.NewFactory/Create, filepath/os/fs, and internal/test.

## Risks And Edge Cases
Skipped when sftp-server is missing; permission assertions assume POSIX-like behavior.

## Test Signals
Broad integration signal for SFTP backend behavior and permission handling.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/sftp/sftp_test.go -->

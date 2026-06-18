<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/sftp/sshcmd_test.go -->
# sources/sync-backup/restic/internal/backend/sftp/sshcmd_test.go

## Purpose
Tests construction of ssh command/argument vectors for SFTP connections.

## Important APIs, Types, And Functions
sshcmdTests and TestBuildSSHCommand are central.

## Control Flow
Table cases cover user/host/port, extra args, custom command, IPv6, and error when command and args are both specified.

## State And Persistence Behavior
No persistence.

## Dependencies And Integration Points
Depends on reflect, testing, and buildSSHCommand.

## Risks And Edge Cases
Does not execute ssh; only validates deterministic argument construction.

## Test Signals
Protects command parsing and option composition used before starting the subprocess.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/sftp/sshcmd_test.go -->

# sources/sync-backup/rsync/errcode.h

## Purpose
Defines rsync process exit codes shared across the codebase, logs, documentation, and cleanup paths.

## Important APIs, Types, and Functions
The header defines `RERR_OK`, syntax/protocol/file-selection errors, socket/file/stream/message/IPC errors, sibling crash/termination codes, signal/wait/memory/partial/vanished/delete-limit codes, timeout codes, and shell/ssh-style command execution codes `RERR_CMD_*`.

## Control Flow
No executable control flow. The numeric constants are consumed by `exit_cleanup()`, protocol/setup errors, IO errors, daemon startup, and command-launch handling.

## State and Persistence Behavior
No runtime state. The numeric values are externally visible process status and therefore persistent compatibility contracts for scripts and users.

## Dependencies and Integration Points
The comment requires synchronization with string mappings in `log.c` and the EXIT VALUES section in `rsync.yo`. Many source files include these constants indirectly through `rsync.h`.

## Risks and Test Signals
Risks are numeric changes breaking automation, undocumented new codes, or stale log/doc mappings. Test signals include exit-code focused tests for syntax errors, protocol mismatch, socket failure, file IO failure, partial transfer, vanished files, delete limit, timeout, and remote command-not-found/run failures.

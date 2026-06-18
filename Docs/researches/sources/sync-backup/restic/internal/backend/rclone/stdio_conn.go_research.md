<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/rclone/stdio_conn.go -->
# sources/sync-backup/restic/internal/backend/rclone/stdio_conn.go

## Purpose
Adapts rclone process stdin/stdout pipes to net.Conn for HTTP/2 transport use.

## Important APIs, Types, And Functions
StdioConn Read, Write, Close, CloseAll, LocalAddr, RemoteAddr, SetDeadline, SetReadDeadline, SetWriteDeadline, Addr, and interface assertion are important.

## Control Flow
Read delegates to receive pipe, Write to send pipe. Close closes send only; CloseAll closes both pipes and kills the command. Deadline methods are unsupported/no-ops with errors where appropriate.

## State And Persistence Behavior
Holds pipe and process references; no repository persistence.

## Dependencies And Integration Points
Depends on io, net, os, os/exec, time, and internal/errors.

## Risks And Edge Cases
HTTP/2 expects net.Conn semantics; missing deadline support can affect timeout behavior, so higher layers use client timeouts and process cleanup.

## Test Signals
Covered indirectly by rclone backend startup/close tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/rclone/stdio_conn.go -->

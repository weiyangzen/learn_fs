<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/rclone/backend.go -->
# sources/sync-backup/restic/internal/backend/rclone/backend.go

## Purpose
Implements the rclone backend by starting `rclone serve restic --stdio` and speaking REST over a single HTTP/2 stdio connection.

## Important APIs, Types, And Functions
rclone struct, NewFactory, run, wrapConn, newBackend, Open, Create, Close, and Properties are central.

## Control Flow
newBackend parses command strings, starts rclone with stdin/stdout pipes, wraps the stdio connection with optional limiter, builds an h2 Transport with a one-shot DialTLSContext, probes a random URL until the server responds, then Open/Create wrap it in the REST backend. Close closes idle h2 connections, waits briefly, then closes pipes if needed.

## State And Persistence Behavior
Repository state is remote through rclone. Local process state includes exec.Cmd, pipes, wait result, HTTP/2 transport, and goroutines reading stderr/waiting.

## Dependencies And Integration Points
Depends on os/exec, pipes, terminal foreground/background handling, HTTP/2, backend/rest, limiter, location, debug/errors/backoff.

## Risks And Edge Cases
Risks include subprocess lifecycle leaks, one-connection HTTP/2 assumptions, command shell splitting, startup timeout/error mapping, and stdio pipe shutdown races.

## Test Signals
backend_test.go and internal_test.go cover availability, failed start, and exit behavior; REST suite covers behavior once connected.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/rclone/backend.go -->

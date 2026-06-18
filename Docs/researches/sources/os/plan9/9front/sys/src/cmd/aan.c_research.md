# File Research: sources/os/plan9/9front/sys/src/cmd/aan.c

Authenticated/reconnecting stream relay that preserves ordered buffered messages across reconnects.

Key responsibilities:
- Runs as client (`-c`) dialing a dialstring or server accepting from an existing net directory.
- Spawns threads for stdin-to-buffer, network-to-stdout, and timer ticks.
- Frames payloads with message number and cumulative ack fields.
- Buffers unsent/unacked messages in Plan 9 channels.
- Detects hung links via periodic sync headers and reconnects for up to `maxto`.
- Resends unacked messages after reconnect through `synchronize()`.

Important behavior:
- `Hdr.nb == 0` with `msg == -1` is a keepalive/sync ack-only frame.
- Incoming messages must match `inmsg`; out-of-order messages are skipped.
- Ack processing returns completed buffers from `unacked` to `empty`.
- EOF from stdin sends a zero-length final message and shuts down after transmission.
- `catch()` exits the process on reconnect timeout alarm.

Dependencies:
- Uses Plan 9 threads/channels, `dial`, `listen`, `accept`, `getnetconninfo`, and big-endian bit macros.

Notable risks:
- Shared globals such as `netfd`, `done`, and counters are manipulated by multiple procs without explicit locks.
- Skipped out-of-order frames rely on retransmission after reconnect rather than local reordering.
- The fixed channel depth limits in-flight buffered data to `Nbuf * Bufsize`.

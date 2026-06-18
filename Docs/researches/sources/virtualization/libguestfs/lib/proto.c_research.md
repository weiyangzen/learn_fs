# File Research: sources/virtualization/libguestfs/lib/proto.c

Client-side RPC protocol and file transfer engine.

Important behavior:
- Defines the call patterns for simple RPC, FileIn, FileOut, and mixed transfer APIs.
- `guestfs_int_send` serializes an XDR message header and optional args, prefixes the message length, checks for stale cancellation/progress, and writes through the current connection.
- `guestfs_int_recv_from_daemon` reads length/flag words, handles launch, cancel, progress, max message size, EOF, and log/progress transparency.
- Receiving `GUESTFS_LAUNCH_FLAG` in LAUNCHING state transitions the handle to READY and emits `GUESTFS_EVENT_LAUNCH_DONE`.
- `child_cleanup` shuts down the backend, frees connection and drives, resets state to CONFIG, and emits subprocess quit.
- File upload uses chunked XDR encoding, handles user cancellation and daemon cancellation, and sends completion or cancel chunks.
- File download opens/creates the target, receives chunks, writes fully, and sends cancellation to the daemon if local write/user cancellation occurs.
- Progress callbacks are represented as four uint64 values and emitted through event callbacks.
- Appliance console log messages are forwarded as appliance events and also inspected for launch progress sentinels.

Filesystem relevance:
- Carries all filesystem RPCs and file upload/download payloads between host library and appliance daemon.

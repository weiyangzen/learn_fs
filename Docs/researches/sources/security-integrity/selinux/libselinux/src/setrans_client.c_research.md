<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/setrans_client.c -->
# sources/security-integrity/selinux/libselinux/src/setrans_client.c

## Purpose
Client-side support for translating raw SELinux contexts to display contexts, display contexts to raw contexts, and raw contexts to color strings via `mcstransd`/setransd.

## Important APIs, Types, And Functions
`selinux_trans_to_raw_context()`, `selinux_raw_to_trans_context()`, and `selinux_raw_context_to_color()` are public entry points. Internals include `setransd_open()`, `send_request()`, `receive_response()`, `raw_to_trans_context()`, `trans_to_raw_context()`, and thread-local one-entry caches.

## Control Flow
Initialization checks for the Unix socket once. If unavailable or disabled at build time, translation degenerates to `strdup()`. Otherwise each cache miss opens a socket, sends a framed request with function ID and NUL-terminated strings, validates a framed response, and caches the result.

## State And Persistence Behavior
State is thread-local cache strings and a pthread destructor key. No persistent storage is changed.

## Dependencies And Integration Points
Uses `SETRANS_UNIX_SOCKET` and protocol constants from `setrans_internal.h`, Unix domain sockets, `readv`/`sendmsg`, optional pthread helpers, and is called by most translated context APIs.

## Risks And Test Signals
Risks include partial `sendmsg()` handling, protocol endian assumptions, socket path limits, stale `has_setrans` after daemon start/stop, cache lifecycle, and fallback masking daemon errors. Tests should cover disabled build, no socket, successful translation, malformed response, oversized response, EINTR, cache hits, and per-thread cleanup.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/setrans_client.c -->

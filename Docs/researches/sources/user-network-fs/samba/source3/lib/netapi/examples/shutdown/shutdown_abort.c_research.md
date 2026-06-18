# sources/user-network-fs/samba/source3/lib/netapi/examples/shutdown/shutdown_abort.c

## sources/user-network-fs/samba/source3/lib/netapi/examples/shutdown/shutdown_abort.c

Purpose: Demonstrates aborting a pending remote shutdown with `NetShutdownAbort()`.

Important APIs/types/functions: Calls `NetShutdownAbort(hostname)`.

Control flow: Parses hostname, submits the abort request, reports libnetapi error strings, and releases resources.

State and persistence behavior: Mutates remote shutdown scheduler state if a shutdown is pending.

Dependencies and integration points: Counterpart to `shutdown_init`.

Risks: Administrative operation with visible system impact. Requires privileges and correct target.

Test signals: Start a delayed shutdown on an isolated test host, abort it, and confirm the host remains up.

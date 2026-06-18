<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/mcstrans/src/mcstransd.c -->
# sources/security-integrity/selinux/mcstrans/src/mcstransd.c

## Purpose

Daemon process for mcstrans. It initializes translation and color state, listens on `/var/run/setrans/.setrans-unix`, accepts libselinux client requests, and serves raw-to-translated, translated-to-raw, and raw-to-color operations. The source was read completely for this report (598 lines).

## Important APIs, Types, and Functions

Important functions are `initialize()`, `process_connections()`, `process_events()`, `service_request()`, `process_request()`, `send_response()`, `cleanup_exit()`, `sighup_handler()`, and `dropprivs()`. Protocol constants identify init, raw-to-trans, trans-to-raw, and color requests; request/response payloads are length-prefixed strings over a Unix stream socket.

## Control Flow

Startup checks root outside DEBUG, opens syslog, loads translations/colors, installs signal handlers, binds/listens the Unix socket, chmods it world-accessible, raises fd limits, drops capabilities, optionally daemonizes, then polls listening and client fds. SIGHUP marks a reload flag that is serviced inside the poll loop.

## State and Persistence Behavior

State includes global `sockfd`, `restart_daemon`, dynamic pollfd arrays, loaded translation/color globals in other modules, and the filesystem socket path. Cleanup frees loaded state and unlinks the socket.

## Dependencies and Integration Points

Depends on libselinux, POSIX sockets/poll/signals/resource limits, libcap, syslog, and local `mcstrans.h`/`mcscolor.h`. It is installed and managed by the systemd service file.

## Risks and Edge Cases

Risks include unauthenticated local socket accessibility, request length validation, partial read/write handling, client fd exhaustion, reload atomicity while serving requests, and privilege/capability assumptions. The source also has dead duplicate `return -1` text in an allocation branch, which is harmless but noisy.

## Test Signals

Signals include foreground daemon smoke tests, libselinux client request tests, SIGHUP reload tests, invalid length/function tests, fd limit tests, and Valgrind/callgrind helper scripts.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/mcstrans/src/mcstransd.c -->

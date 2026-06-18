# File Research: sources/virtualization/nbdkit/server/socket-activation.c

This file handles systemd-style socket activation. On POSIX, `get_socket_activation` checks `LISTEN_PID`, validates it matches the current process, parses `LISTEN_FDS`, limits accepted descriptors to `1..16`, marks inherited descriptors close-on-exec, and records each descriptor plus optional name from `LISTEN_FDNAMES`.

Names are colon-separated. Empty or `"unknown"` names are treated as absent. Invalid descriptors or allocation failures are fatal startup errors. At exit from parsing, the socket activation environment variables are unset to avoid leaking them to child processes.

Windows has a no-op implementation. `free_socket_activation` frees copied names and resets the socket activation vector.

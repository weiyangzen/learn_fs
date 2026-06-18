# sources/sync-backup/bup/lib/bup/cmd/daemon.py

## Purpose
Implements `bup daemon`, a TCP listener that accepts bup protocol connections and spawns `bup mux -- bup server` for each connection.

## Important APIs, Types, and Functions
Defines `optspec` and `main`. Uses `socket.getaddrinfo`, `SO_REUSEADDR`, `listen`, `select.select`, `os.dup`, `fcntl.FD_CLOEXEC`, `subprocess.Popen`, `path.exe`, and logging helpers.

## Control Flow
Parses listen address and port, creates listen sockets for all address families returned by `getaddrinfo`, sets close-on-exec on listeners, loops with 60-second select, accepts connections, duplicates the socket fd for stdin/stdout of the spawned mux/server process, and closes duplicates in the parent.

## State and Persistence Behavior
Maintains listening sockets and child server processes; no file persistence. Network connections carry repository protocol state handled by the spawned server.

## Dependencies and Integration Points
Integrates with `bup mux`, `bup server`, TCP clients (`Client.ViaBup`), and bup path resolution.

## Risks and Test Signals
Risks include bug-prone error reporting when no sockets are created (`e` remains `None`), fd lifecycle issues, unbounded child process spawning, and shutdown exceptions on already-closed sockets. Signals are successful listen logs, accepted connection logs, client protocol success, and clean socket close.

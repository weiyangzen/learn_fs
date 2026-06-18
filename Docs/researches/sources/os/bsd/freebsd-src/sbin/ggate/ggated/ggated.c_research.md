# File Research: sources/os/bsd/freebsd-src/sbin/ggate/ggated/ggated.c

`ggated.c` implements the GEOM Gate TCP server. It exports local files/devices listed in an exports file, validates remote clients, and services protocol requests against the backing object.

Key behavior:
- Default exports file is `/etc/gg.exports`.
- Parses export lines as remote IP or host with optional CIDR mask, flags, and path.
- Supports export access flags `ro`, `rd`, `wo`, `rw`, plus `direct` and `nodirect`.
- Validates each incoming client by source address, requested path, requested access mode, and direct-I/O policy.
- Uses the shared ggate handshake: receives version, validates magic/version, receives `g_gate_cinit`, and responds with `g_gate_sinit`.
- Pairs two sockets into a `ggd_connection` by token. Incomplete connections older than 10 seconds are cleaned up.
- Once both sockets are present, forks a child process for that connection, removes it from the parent list, and lets the child serve I/O.
- Child process creates three threads:
  - `recv_thread()` receives protocol headers and write data, then queues requests.
  - `disk_thread()` performs `pread`, `pwrite`, or `fsync` against the exported object.
  - `send_thread()` sends completion headers and read data back to the client.
- Uses queue mutexes and condition variables for request handoff.
- Supports daemon mode, pidfile management, bind address selection, custom port, socket buffer tuning, verbose foreground mode, and SIGHUP export reload.

Important details:
- Request bounds and alignment are enforced with assertions in `disk_thread()`.
- Short reads/writes are reported as `EIO` when errno is otherwise zero.
- `BIO_FLUSH` maps to `fsync()`.
- `malloc_waitok()` retries allocations indefinitely for per-request memory.
- SIGHUP reload is processed in the accept loop before handling the next connection.

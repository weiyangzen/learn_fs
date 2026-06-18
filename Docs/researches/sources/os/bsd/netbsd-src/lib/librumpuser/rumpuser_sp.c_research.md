# File Research: sources/os/bsd/netbsd-src/lib/librumpuser/rumpuser_sp.c

## Purpose
Implements the server side of rump sysproxy: a socket RPC bridge that lets a remote client issue rump-kernel syscalls and memory-copy requests through a host socket connection.

## Main Interfaces
Exports `rumpuser_sp_init`, `rumpuser_sp_fini`, `rumpuser_sp_copyin`, `rumpuser_sp_copyinstr`, `rumpuser_sp_copyout`, `rumpuser_sp_copyoutstr`, `rumpuser_sp_anonmmap`, and `rumpuser_sp_raise`.

## Control Flow And State
The file includes `sp_common.c` directly for shared protocol framing and socket helpers. Global server state includes a pollfd array, parallel `spclient` array, disconnect counter, shutdown flag, worker limits, and protocol banner.

`rumpuser_sp_init` parses a `tcp://` or `unix://` URL, creates/binds/listens on a socket, builds a `RUMPSP-0.4-...` banner, and launches a detached `spserver` thread. The server initializes client slots, polls the listener and clients, accepts connections, sends the banner, and reads framed requests.

Client handshakes support new guest creation, fork attachment via one-time prefork auth tokens, and exec handshakes. Prefork uses random 128-bit auth tokens and a global list protected by `pfmtx`.

Syscall and exec requests are bounced to detached worker threads. Workers call rump hypervisor hooks to create LWPs, execute syscalls, release LWPs, or drain/notify exec. Worker pool state is controlled by `sbamtx`, `sbacv`, `nworker`, `idleworker`, and `nwork`.

Copyin/copyinstr and anonymous mmap are synchronous request/response operations sent from the server back to the client. Copyout and signal raise are asynchronous outbound requests. These paths unschedule the rump kernel before blocking on socket I/O and reschedule afterward.

Disconnect handling marks clients dying, wakes waiters, releases main LWPs unless exec owns them, resets per-connection fields, closes fds, and notifies the main loop through `signaldisco`.

## Dependencies
Depends on pthreads, sockets, `poll`, fcntl nonblocking mode, rump hypervisor callbacks, `rumpuser_getrandom`, and shared protocol definitions from `sp_common.c`.

## Risks And Notes
The protocol is explicitly ABI-dependent; client and server must agree on C layouts and pointer-sized fields. Blocking sends are noted as problematic for the main thread. The prefork and exec paths rely on careful refcount and LWP ownership ordering to avoid using released process contexts. URL parsing and socket cleanup are delegated to the shared common file.

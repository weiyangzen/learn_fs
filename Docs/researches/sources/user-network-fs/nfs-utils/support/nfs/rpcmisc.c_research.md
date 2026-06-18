# sources/user-network-fs/nfs-utils/support/nfs/rpcmisc.c

Purpose: legacy RPC service startup helper with inetd/portmapper awareness and closedown timer behavior.

Important APIs and globals: `rpc_init()` registers UDP/TCP transports for a program/version. Globals `_rpcpmstart`, `_rpcprotobits`, and `_rpcsvcdirty` control inetd mode, enabled protocols, and idle shutdown. Internal `makesock()` binds IPv4 sockets and `closedown()` exits idle portmapper-started services.

Control flow: `rpc_init()` detects whether fd 0 is an inetd-provided socket and sets protocol bits accordingly. Without inetd, it unregisters old mappings and creates UDP/TCP sockets or RPC_ANYSOCK transports. It reuses last UDP/TCP transport for additional versions on the same port, registers each with `svc_register()`, and sets SIGALRM closedown in portmapper-start mode.

State and persistence: process-global protocol/dirty/start flags and static last transports. Registers/unregisters with local portmapper/rpcbind persistent runtime registry.

Dependencies and integration: used when libtirpc `nfs_svc_create()` is unavailable or by legacy service setup. Depends on `svc_socket.c`, `rpcmisc.h`, RPC/pmap APIs, and `nfslib.h`.

Risks: IPv4-only. Signal handling uses `signal()` and `alarm()` with global state. Fatal logging exits on many setup failures. Reusing `last_transp` depends on port equality and can be surprising when protocol bits change.

Test signals: inetd UDP/TCP detection, explicit fixed port, random port, multi-version reuse, protocol-bit filtering, idle closedown with clean/dirty service state, and bind/listen failures.

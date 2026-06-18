<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/dbench/tbench_srv.c -->
# sources/test-tools/xfstests-bld/fstests-bld/dbench/tbench_srv.c

Source read: complete file, 114 lines, 2225 bytes, sha256 `6d51a3696ec0809d08e020337ac1795850e4fc4554d42834036fed3e8bfee3de`. Final split target: `Docs/researches/sources/test-tools/xfstests-bld/fstests-bld/dbench/tbench_srv.c_research.md`.

Purpose: standalone tbench server that accepts synthetic SMB-size requests from `sockio.c` clients and replies with payloads of the requested size. It is the network counterpart for throughput benchmarking.

Important APIs/types/functions: global `struct options options` defaults `tcp_options` to `TCP_OPTIONS`; `process_opts()` supports `-t` to override socket options; `listener()` opens/listens on `TCP_PORT`, accepts connections, and forks per client; `server(fd)` performs the packet echo protocol.

Control flow: `main()` parses options and enters `listener()` forever. The listener ignores `SIGCHLD`, reaps exited children opportunistically, accepts connections, forks a child to run `server(fd)`, and closes the accepted fd in the parent. Each server child ignores `SIGPIPE`, reads a 4-byte request length, reads that payload, reads response length from the second word, writes a response header plus requested payload, and exits on disconnect or malformed oversized input.

State and persistence behavior: maintains live sockets and forked child processes only. It writes progress markers to stdout and does not persist files.

Dependencies and integration: uses `socklib.c` for socket setup and full reads/writes, `dbench.h` for constants and networking headers, and the packet format expected by `sockio.c`.

Risks: no authentication, IPv4-only listener on all interfaces, unbounded accept loop, fork-per-connection scaling, and fixed 70000-byte buffer. If `open_socket_in()` fails, `listen(-1, ...)` will fail with a generic message rather than reporting bind reason.

Test signals: start the server and connect a tbench client; verify `waiting for connections`, per-client `^` markers, stable throughput, and no `overflow in server!` for representative trace sizes. Port-conflict and socket-option tests should exercise failure paths.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/dbench/tbench_srv.c -->

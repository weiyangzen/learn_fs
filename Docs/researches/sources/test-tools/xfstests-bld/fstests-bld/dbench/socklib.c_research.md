<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/dbench/socklib.c -->
# sources/test-tools/xfstests-bld/fstests-bld/dbench/socklib.c

Source read: complete file, 222 lines, 5487 bytes, sha256 `1b07fb88009edc39665c8891ba4bc5e9457da2a1ae47906530a4ecc8404225be`. Final split target: `Docs/researches/sources/test-tools/xfstests-bld/fstests-bld/dbench/socklib.c_research.md`.

Purpose: socket utility library for dbench/tbench. It opens inbound/outbound TCP sockets, applies configurable socket options, and provides read/write loops that transfer a requested byte count.

Important APIs/types/functions: `open_socket_in(type, port)` creates, sets `SO_REUSEADDR`, binds to all IPv4 addresses, and applies configured options; `open_socket_out(host, port)` resolves with `gethostbyname()`, connects, and applies options; `set_socket_options(fd, options)` parses comma/space-separated option tokens using `next_token()`; `read_sock()` and `write_sock()` loop over `recv()`/`send()`.

Control flow: socket option parsing optionally accepts `NAME=value`, looks up tokens in `socket_options[]`, decides whether to pass caller value or predefined value, calls `setsockopt()`, and logs unknown/failed options without aborting. Read/write loops advance buffer pointers until the requested size is transferred or a nonpositive syscall result occurs.

State and persistence behavior: creates sockets and kernel socket option state. No local persistence. Errors are returned as `-1` for opens or partial byte counts for transfer loops.

Dependencies and integration: includes `dbench.h` for networking headers, `options.tcp_options`, `BOOL`, and `next_token()`. Used by `sockio.c` clients and `tbench_srv.c` listener/server.

Risks: uses legacy IPv4-only `gethostbyname()` and does not close the socket on hostname resolution failure. `open_socket_in()` returns `-1` on bind failure without closing. `SO_SNDTIMEO`/`SO_RCVTIMEO` are treated as integer options though many platforms expect `struct timeval`. Error handling logs but often continues, so misconfigured TCP options can be silent performance variables.

Test signals: unit-style smoke tests can bind/listen/connect on localhost, set `TCP_NODELAY SO_REUSEADDR`, and verify full-size transfers. Negative tests should cover unknown options, failed DNS, occupied port bind, and server disconnects.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/dbench/socklib.c -->

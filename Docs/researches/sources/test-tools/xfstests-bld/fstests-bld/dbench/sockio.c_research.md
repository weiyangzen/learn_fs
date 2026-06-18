<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/dbench/sockio.c -->
# sources/test-tools/xfstests-bld/fstests-bld/dbench/sockio.c

Source read: complete file, 250 lines, 5889 bytes, sha256 `2d7fee80c98abf7b7183d38b60ad4e5dea0dd83c56f2bdce737ef4d0227d1297`. Final split target: `Docs/researches/sources/test-tools/xfstests-bld/fstests-bld/dbench/sockio.c_research.md`.

Purpose: implements the tbench client-side socket replay backend. It maps the same `nb_*` trace-operation API used by dbench onto synthetic SMB-like request/response packet exchanges with a tbench server instead of local filesystem calls.

Important APIs/types/functions: `struct sockio` stores a 70000-byte packet buffer and connected socket fd in `child->private`; `do_packets()` sends a request with encoded send/receive sizes and validates the response header; `nb_setup()` connects to `options.server` on `TCP_PORT`, applies TCP options, and performs an initial small exchange. All exported `nb_*` operations compute operation-specific packet sizes and call `do_packets()`.

Control flow: setup opens a TCP connection and initializes per-child rate state. Each trace callback ignores most semantic fields and models wire cost by calculating an approximate SMB packet size from path length, data size, or result count. Read/write callbacks update `child->bytes`; sleep delegates to `usleep()`. Cleanup/deltree are no-ops because the backend has no local filesystem tree.

State and persistence behavior: persistent state is network-side only: a live TCP connection per child and byte counters in `child_struct`. No files are created locally by this backend.

Dependencies and integration: depends on `socklib.c` for connect, socket options, and robust read/write; depends on `tbench_srv.c` for the echo-like server protocol; shares API names with `fileio.c`, making it a link-time alternative backend for the same trace runner.

Risks: the 70000-byte buffer bounds are implicit; large trace sizes could exceed it. `MSG_TRUNC` behavior with stream sockets is platform-sensitive. Protocol validation checks only payload size, not operation identity or content. Fatal `exit(1)` on short I/O makes transient network failures abort the whole client.

Test signals: run `tbench_srv`, then tbench clients with representative load files and TCP options. Useful signals include stable packet synchronization, expected aggregate throughput, no buffer overflow diagnostics, and byte counter agreement for read/write-heavy traces.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/dbench/sockio.c -->

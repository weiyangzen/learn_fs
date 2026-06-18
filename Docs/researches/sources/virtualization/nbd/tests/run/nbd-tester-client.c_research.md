# File Research: sources/virtualization/nbd/tests/run/nbd-tester-client.c

## Purpose
Implements a standalone protocol test client for exercising `nbd-server` without attaching a kernel NBD device.

## Main Entry Points
- `main()` parses test options, opens TCP/Unix/inetd-mode connections, chooses a test function, and runs it.
- `setup_connection_common()` performs initial NBD handshake, optional STARTTLS, export selection, and export-info reading.
- `throughput_test()` streams read or write requests over the whole export, optionally injecting FLUSH and FUA.
- `oversize_test()` verifies server behavior around large read sizes.
- `handshake_test()` sends an unsupported negotiation option and expects a proper `NBD_REP_ERR_UNSUP`, then aborts.
- `integrity_test()` replays a transaction trace while tracking expected block contents and in-flight ordering.
- Helpers manage request-context lists, buffered socket writes, exact reads/writes, generated block contents, cookie uniqueness, and connection shutdown.

## Control Flow
The client can connect by hostname/port, Unix socket, or by launching a server command in inetd mode over a socketpair. It validates `INIT_PASSWD`, option magic, fixed-newstyle flags, optional TLS negotiation, export name selection, export size, and server flags. Tests then send raw NBD request packets and validate reply headers/data.

The integrity test maps a temporary per-block state array, reads a transaction log, rewrites cookies to unique random values, generates deterministic 512-byte data for writes, verifies reads against the last successful write sequence, and prevents unsafe overlapping in-flight requests unless loose ordering is requested.

## Dependencies
Uses POSIX sockets, select, mmap, temporary files, GLib logging/hash tables, local `cliserv.h`, optional GnuTLS wrapper code through `crypto-gnutls.h`, and NBD protocol constants.

## Risks and Notes
The tool deliberately notes that passing here is not equivalent to kernel-client compatibility. It mostly validates ordinary reply mode, not the full structured-reply feature set. Several diagnostics are stored in a global fixed-size `errstr` buffer.

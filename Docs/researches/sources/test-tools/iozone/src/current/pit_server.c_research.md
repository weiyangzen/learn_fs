# sources/test-tools/iozone/src/current/pit_server.c

Purpose: IPv4/IPv6 TCP and UDP "Programmable Interdimensional Timer" server that returns the current timestamp in microseconds as a decimal string. It is used by iozone as a lightweight timing service.

Important APIs/types/functions: `main` parses `-v` and required `-p service`; `openSckt` uses `getaddrinfo`, `socket`, `setsockopt(IPV6_V6ONLY)`, `bind`, and `listen` to open passive sockets; `pit` uses `poll`, `accept`, `shutdown`, `write`, `recvfrom`, `sendto`, `gettimeofday`, and Windows `QueryPerformanceCounter` alternatives. Macros include `DFLT_SERVICE`, `MAXTCPSCKTS`, `MAXUDPSCKTS`, `VALIDOPTS`, `USAGE`, and `CHK`.

Control flow: `main` defaults the service name to `PIT` but requires `-p`, opens both TCP and UDP socket arrays for the requested service, and enters `pit` when at least one socket exists. `openSckt` clears descriptor slots, sets hints for TCP or UDP, walks address records, optionally prints address metadata, creates sockets, enforces IPv6-only behavior when available, binds, listens for TCP, and records descriptors. `pit` builds a `pollfd` array covering TCP sockets followed by UDP sockets, waits forever, computes the current microsecond counter once per poll wakeup, and sends that string to each ready TCP connection or UDP sender.

State/persistence behavior: process-local state includes global verbose flag, host/service formatting buffers, `timeStr`, and socket descriptors. The server has no durable state and never returns from the main loop under normal operation. Each request gets the timestamp captured before the ready-socket loop, so multiple ready clients in one poll cycle receive the same value.

Dependencies/integration: depends on network database APIs, POSIX sockets, `poll`, `gettimeofday`, and platform branches for Windows and SUA. `/etc/services` may define `PIT`, but `-p` can pass a numeric or named service to `getaddrinfo`. The iozone makefile builds this helper for many platform targets.

Risks/test signals: global `service_name[20]` is filled with `strcpy(optarg)` and can overflow on long service names. `CHK` exits the whole daemon on many transient network errors. Partial TCP/UDP send loops advance `wBytes` but always pass `timeStr` rather than `timeStr + bytes_sent`, so rare partial writes can repeat the beginning of the timestamp. Verbose code contains duplicated fragments that may affect compilation. Smoke tests should bind an ephemeral port, query over TCP and UDP, validate numeric microsecond strings, and verify IPv4/IPv6 behavior when available.

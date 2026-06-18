# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/libunbound/unbound.h

Main public libunbound API header.

Defines:
- Version macros filled by build configuration.
- Opaque `struct ub_ctx`.
- `struct ub_result`: public query result with original qname/type/class, RDATA array and lengths, canonical name, rcode, answer packet, havedata/NXDOMAIN/security/bogus flags, bogus reason, rate-limit flag, and TTL.
- `ub_callback_type` for asynchronous `ub_resolve_async()`.
- `enum ub_ctx_err`: public error codes such as no error, socket, nomem, syntax, servfail, fork failure, after-finalize config change, init failure, pipe error, readfile error, and unknown async id.

Context/configuration API:
- Create/delete contexts.
- Set/get unbound.conf-style options.
- Load config files, resolv.conf, and hosts files.
- Configure forwarding, DNS-over-TLS forwarding, stub zones, debug output/level, trust anchors, trust-anchor files, RFC5011 autotrust files, and BIND-style trusted-keys files.
- Enable asynchronous threaded/forked behavior with `ub_ctx_async()`.

Resolution API:
- `ub_resolve()` for blocking resolution.
- `ub_resolve_async()` for callback-based async resolution.
- `ub_poll()`, `ub_wait()`, `ub_fd()`, and `ub_process()` for non-threaded async result processing.
- `ub_cancel()` cancels in-flight async queries.
- `ub_resolve_free()` releases results.
- `ub_strerror()` and `ub_version()` provide diagnostics/versioning.

Local authority helpers:
- Print local zones.
- Add/remove local zones.
- Add/remove local data.

Statistics:
- `struct ub_shm_stat_info` exposes shared-memory global stats and memory buckets.
- `struct ub_server_stats` exposes per-worker query, cache, protocol, DNSSEC, DNSCrypt, auth-zone, subnet, cachedb, RPZ, QUIC, and timeout counters.
- `struct ub_stats_info` wraps server stats plus mesh counters and reply timing data.

Role:
- This is API contract documentation and declarations, not implementation.
- It describes libunbound’s supported usage modes: blocking, nonblocking fd polling, threaded async, forked async, and shared-context threaded blocking.

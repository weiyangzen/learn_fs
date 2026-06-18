# File Research: sources/os/bsd/netbsd-src/lib/libwrap/tcpd.h

## Summary
Central public/internal TCP wrappers header defining request metadata, host metadata, request update keys, evaluation APIs, socket hooks, global configuration, and non-local access-control result codes.

## Main Responsibilities
- Define `struct host_info` and `struct request_info`.
- Define string constants and case-insensitive comparison macros.
- Declare libwrap public entry points such as `hosts_access()`, `hosts_ctl()`, `request_init()`, `request_set()`, `eval_*()`, `process_options()`, `shell_cmd()`, `percent_x()`, and `rfc931()`.
- Define request update keys `RQ_FILE`, `RQ_DAEMON`, `RQ_USER`, client/server name/address/sockaddr keys.
- Define `AC_PERMIT`, `AC_DENY`, and `AC_ERROR`.

## Integration Notes
This header is shared by libwrap modules and callers that populate `request_info`. It aliases `fromhost` to `sock_host` when TLI support is not needed.

## Risks
The structures contain fixed-size strings and cached pointers to socket addresses. Callers must initialize them through `request_init()` or maintain the same invariants manually.

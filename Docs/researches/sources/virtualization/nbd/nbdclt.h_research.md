# File Research: sources/virtualization/nbd/nbdclt.h

## Purpose
Declares client-side configuration structures used by `nbd-client` and the `nbdtab` parser.

## Main Contents
- `CLIENT` stores parsed client options: export name, device, host/port, TLS files, block size, timeouts, connection count, forced size, option flags, persist-mode settings, and priority string.
- Parser callback declarations: `nbdtab_set_property()`, `nbdtab_set_flag()`, `nbdtab_commit_line()`, and `yyerror()`.
- `saved_connection_t` and `persist_connection_t` hold connection and negotiated metadata for persistent/reconnect behavior.

## Dependencies
Uses `struct addrinfo`, fixed-width integer types, and `bool`; including files must provide the corresponding headers.

## Risks and Notes
This header is a shared data contract for parser and client code, so changes to `CLIENT` fields affect argument parsing, `nbdtab` parsing, and tests.

# File Research: sources/os/bsd/freebsd-src/sbin/dhclient/dhcpd.h

## Purpose
Shared dhclient internal header. It centralizes system includes, core data structures, global variables, path defaults, and cross-file function prototypes.

## Main Elements
- Core structs:
  - `option_data`, `string_list`, `iaddr`, `iaddrlist`.
  - `packet`: parsed packet wrapper around `struct dhcp_packet`.
  - `hardware`, `client_lease`, `client_config`, `client_state`, `interface_info`.
  - `timeout` and `protocol` event-loop nodes.
  - `hash_bucket` and `hash_table`.
- State enum: `S_REBOOTING`, `S_INIT`, `S_SELECTING`, `S_REQUESTING`, `S_BOUND`, `S_RENEWING`, `S_REBINDING`.
- Defaults and paths: DHCP ports, `_PATH_DHCLIENT_CONF`, `_PATH_DHCLIENT_DB`, log facility, time limits.
- Prototypes for option handling, parser/lexer, allocation, BPF I/O, dispatch, hash, tables, conversion, inet helpers, dhclient state/lease/script functions, packet assembly, config parsing, and privsep buffers.
- Globals: `capsyslog`, config/lease paths, time globals, top-level config, pidfile, and active interface.

## Dependencies And Integration
Included by almost every dhclient C file. It forms the compile-time contract between the protocol engine, parser, option tables, network I/O, and privilege-separated script runner.

## Risk Notes
Because this header exposes mutable global structures and fixed-size arrays, ABI/layout changes affect nearly every file. Option arrays are indexed by raw DHCP option code and require bounds discipline throughout the codebase.

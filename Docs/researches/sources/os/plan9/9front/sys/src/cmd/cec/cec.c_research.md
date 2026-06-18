# File Research: sources/os/plan9/9front/sys/src/cmd/cec/cec.c

Coraid Ethernet Console client using a custom Ethernet protocol.

Key behavior:
- Parses options for escape character, target Ethernet address, host, shelf, service posting, debug, and persistent probing.
- Can post itself under `/srv` and run over a pipe for service-style use.
- Opens a Plan 9 Ethernet interface, probes shelves by broadcasting discovery packets, records offers in a sorted table, and optionally lets the user choose a target.
- Maintains packet headers with custom EtherType `0xbcbc`, connection id, sequence, type, and payload length.
- Implements timeout helpers via `alarm`/notes.
- Provides byte-order helpers for Ethernet packet fields.
- Connection loop multiplexes keyboard input and CEC network packets, handles acknowledgements/data/reset/discovery traffic, escape handling, and clean exit paths.
- `exits0` centralizes raw-mode cleanup and exit behavior.

Dependencies:
- Includes Plan 9 libc, `ip.h` for Ethernet address formatting/parsing, and `cec.h`.
- Uses platform networking functions from `plan9.c`, mux helpers from `mux.c`, and raw console helpers from `utils.c`.

Research notes:
- This is a low-level console-over-Ethernet program, not IP/TCP.
- The default escape character is control-backslash.

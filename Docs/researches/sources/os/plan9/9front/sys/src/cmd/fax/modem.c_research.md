# File Research: sources/os/plan9/9front/sys/src/cmd/fax/modem.c

## Purpose
Implements low-level modem I/O and response parsing for the fax tools.

## Key Elements
Maps terse and verbose modem result codes to internal results, initializes modem descriptors, buffers raw input, polls available bytes through `dirfstat(fd)->length`, reads single characters and CRLF-terminated lines with timeouts, writes AT commands, parses responses including fax status callbacks, and toggles XON/XOFF through the connection control fd.

## Dependencies
Uses Plan 9 file descriptors, Bio buffering, syslog-style verbose hooks, and the fax-specific response handlers in `fax2modem.c`.

## Behavior/Risks
Input readiness depends on Plan 9 device length semantics. `response` ignores unknown lines until timeout and treats checksum-free modem text as trusted. The comment notes line lengths/newlines are not fully checked.

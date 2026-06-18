# File Research: sources/os/bsd/freebsd-src/sbin/ipf/ipsend/ipsopt.c

This file builds IPv4 option bytes for the `ipsend` command.

It defines supported option names (`eol`, `nop`, `rr`, `ts`, security level, `lsrr`, `satid`, `ssrr`) and security level names. `ipseclevel()` maps security level text to option values.

`addipopt()` appends a specific option to an option buffer, supporting route-record length overrides, timestamps, security labels, source-route address lists, and SATID values. `buildopts()` parses a comma-separated option string, avoids duplicate option classes through a bitmask, appends padding and EOL/NOP bytes, and returns final option length.

Important dependencies include `ipsend.h`, `netinet/ip_var.h`, and TCP/IP option constants.

Implementation notes and risks:
- Parsing mutates the option string via `strtok()` and embedded `=`/`,` splitting.
- Maximum option length is capped at 48 bytes.
- Source-route parsing only accepts numeric IPv4 strings through `inet_addr()`.

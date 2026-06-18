# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/optname.c

IP option-name parser for rule text.

Key behavior:
- Parses comma-separated IPv4 option names into an option bitmask.
- Handles `sec-class` specially by consuming the following argument as security levels.
- Reports unknown option/security names with line numbers.

Research notes:
- Mutates the current argument through `strtok()`.

# sources/test-tools/strace/src/ioperm.c

Decoder for `ioperm`. It prints starting port, number of ports, and enable flag, returning decoded. State is syscall arguments only. Dependencies are integer printers and `defs.h`. Risks are minimal; the main concern is unsigned range formatting for port/count and boolean enable readability. Tests should cover enabling/disabling ranges, zero length, large port ranges, and permission failures.

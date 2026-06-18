# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/addipopt.c

This helper appends one IPv4 option to an option buffer for shared IPFilter tooling.

`addipopt()` validates the 48-byte option limit, writes the option value and length/min-offset fields, and handles option-specific class data for security level, RR/TS length, LSRR/SSRR route address, and SATID. In debug mode it prints option metadata.

Important dependencies include global `ionames`, `seclevel()`, global `opts`, and IP option constants from `ipf.h`.

It mutates the caller-provided option buffer and returns only the number of bytes added.

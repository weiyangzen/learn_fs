# File Research: sources/os/bsd/freebsd-src/sbin/ddb/Makefile

## Purpose
Builds the `ddb` userland control utility and installs default DDB configuration.

## Main Elements
- `CONFS=ddb.conf`
- `PACKAGE=runtime`
- `PROG=ddb`
- `SRCS=ddb.c ddb_capture.c ddb_script.c`
- `MAN=ddb.8`
- `LIBADD=kvm`

## Dependencies And Integration
Links `libkvm` for crash-dump capture-buffer access.

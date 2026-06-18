# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/smallprimes.c

Defines a global `ulong smallprimes[1000]` table. It includes `os.h`.

The table is the first 1000 small prime numbers, used as shared prime data by other `libsec` code. This file contains data only: no functions, allocation, or control flow.

Its Makefile entry includes it in `libsec.a`, making the symbol available to code that declares the table externally.

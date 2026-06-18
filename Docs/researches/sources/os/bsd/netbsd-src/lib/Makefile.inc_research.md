# File Research: sources/os/bsd/netbsd-src/lib/Makefile.inc

Shared make include for libraries under `lib`. It only sets the default warning level with `WARNS?= 5`.

This acts as a small policy default inherited by subordinate library builds unless overridden.

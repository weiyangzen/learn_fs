# File Research: sources/os/plan9/plan9/sys/src/cmd/bzip2/lib/bzfeof.c

Small stdio helper for libbzip2.

Defines `bz_feof(FILE *f)`, which probes EOF by reading one byte with `fgetc()` and pushing it back with `ungetc()` when not EOF.

Used by the stdio-oriented bzip2 wrapper layer split out elsewhere in this Plan 9 port.

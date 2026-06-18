# File Research: sources/os/linux/linux-stable/fs/nfsd/trace.c

## Summary
Tracepoint definition unit for NFSD.

## Contents
Defines `CREATE_TRACE_POINTS` and includes `trace.h`, causing the tracepoint declarations in the header to instantiate storage and registration metadata in exactly one compilation unit.

## Risks
This file must remain minimal. Duplicating `CREATE_TRACE_POINTS` in another NFSD source file would create duplicate tracepoint definitions; removing this file would leave trace events declared but not defined.

# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ulimit.h

## Purpose
Legacy `ulimit(2)` command definitions.

## Main Interfaces
- Defines command constants for querying and setting file size and related process limits, including historical forms such as `UL_GETFSIZE`, `UL_SETFSIZE`, `UL_GMEMLIM`, `UL_GDESLIM`, and `UL_GTXTOFF`.

## Dependencies And Relationships
Used by libc and syscall compatibility for the legacy `ulimit` interface. Modern code generally uses `getrlimit`/`setrlimit`.

## Research Notes
This header preserves old command values for source and binary compatibility.

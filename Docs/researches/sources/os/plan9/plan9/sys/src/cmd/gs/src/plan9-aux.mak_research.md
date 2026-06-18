# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/plan9-aux.mak

Auxiliary makefile for Ghostscript’s Unix-style platform and helper-program rules, adapted in this Plan 9 source tree.

Although the internal identifier is `unix-aux.mak`, this file appears as `plan9-aux.mak` in the Plan 9 Ghostscript source directory. It defines:

- `unix_.dev` and `sysv_.dev` platform modules from `gp_getnv`, `gp_unix`, `gp_unifs`, `gp_unifn`, `gp_stdia`, optional cache code, and `nosync`.
- Build rules for platform support objects such as `gp_unix`, `gp_unix_cache`, `gp_stdia`, and `gp_sysv`.
- Auxiliary program build rules for `echogs`, `genarch`, `genconf`, `gendev`, `genht`, and `geninit`.
- `gconfig_.h` generation by probing headers under `INCLUDE=/sys/include/ape`, including `dirent.h`, `sys/time.h`, `sys/times.h`, and JPEG memory-system availability.

This is build support for Ghostscript in a Unix/APE-like environment. It touches filesystem paths only to test for headers and generate build artifacts.

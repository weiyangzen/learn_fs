# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/unix-aux.mak

Common Unix partial makefile for platform modules and auxiliary build tools.

Key points:
- Defines `UNIX_AUX_MAK`.
- Builds `unix_.dev` from Unix platform objects including `gp_getnv`, `gp_unix`, `gp_unifs`, `gp_unifn`, `gp_stdia`, and `gp_unix_cache`, including `nosync`.
- Builds `sysv_.dev` for older System V platforms using `gp_sysv`.
- Defines compilation rules for Unix platform objects and build tools: `echogs`, `genarch`, `genconf`, `gendev`, `genht`, and `geninit`.
- Generates `gconfig_.h` by probing `/usr/include` for directory/time headers and checking for `jmemsys.h`.

Dependencies and interactions:
- Included by Unix top-level makefiles before linking.
- Produces generated config headers consumed by wrapper headers and platform modules.

Research relevance:
- Encodes Unix platform abstraction and configure-lite behavior for non-autoconf builds.

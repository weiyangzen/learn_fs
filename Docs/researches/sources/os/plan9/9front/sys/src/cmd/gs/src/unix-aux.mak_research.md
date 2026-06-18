# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/unix-aux.mak

Common Unix makefile fragment for platform modules and auxiliary build tools.

Key points:
- Defines Unix platform module `unix_.dev` from `gp_getnv`, `gp_unix`, `gp_unifs`, `gp_unifn`, `gp_stdia`, and `gp_unix_cache`, including `nosync`.
- Defines older System V platform module `sysv_.dev` using `gp_sysv`.
- Provides object compile rules for Unix platform source files.
- Builds auxiliary generators: `echogs`, `genarch`, `genconf`, `gendev`, `genht`, and `geninit`.
- Generates `gconfig_.h` by probing `/usr/include` for directory/time headers and local JPEG memory headers.
- Includes comments about Ultrix `sh -e` behavior and old optimizer issues.

Dependencies and interactions:
- Included by Unix top-level makefiles and the library test makefile.
- Produces generated config headers consumed by core Ghostscript sources.
- Assumes `$(ECHOGS_XE)` is available for generated text output.

Research relevance:
- Central to the Unix portability layer: platform abstraction objects, generated feature headers, and build-time helper tools all originate here.

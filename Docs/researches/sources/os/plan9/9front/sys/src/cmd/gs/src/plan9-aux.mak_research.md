# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/plan9-aux.mak

Plan 9-adapted auxiliary makefile fragment, derived from Ghostscript’s Unix auxiliary make rules. It builds Unix-like platform modules and helper programs for the Plan 9/APE environment.

It defines `unix_.dev` from `gp_getnv`, `gp_unix`, `gp_unifs`, `gp_unifn`, `gp_stdia`, and `gp_unix_cache`, plus a `sysv_.dev` variant. It builds helper executables (`echogs`, `genarch`, `genconf`, `gendev`, `genht`, `geninit`) and generates `gconfig_.h` by probing `/sys/include/ape` for headers such as `dirent.h`, `sys/time.h`, and `sys/times.h`.

Dependencies include APE headers, Unix compatibility platform code, MD5 cache support, and the generic Ghostscript build variables.

Filesystem relevance is modest but real for 9front userland: it probes Plan 9 APE include files and selects Unix-style file/path support modules for Ghostscript.

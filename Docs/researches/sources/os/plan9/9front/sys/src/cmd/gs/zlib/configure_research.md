# File Research: sources/os/plan9/9front/sys/src/cmd/gs/zlib/configure

## Purpose
Hand-written zlib configuration script for compiler flags, shared-library support, install paths, and generated config files.

## Key Elements
Parses `--shared`, `--prefix`, `--exec_prefix`, `--libdir`, and `--includedir`. Detects zlib version from `zlib.h`, chooses compiler/linker flags for gcc and many Unix variants, tests shared library creation, probes `unistd.h`, printf-family availability and return values, `errno.h`, `mmap`, and assembler symbol underscores.

## Behavior/Risks
Writes temporary `ztest$$` files, generates `zconf.h` from `zconf.in.h`, and rewrites `Makefile` from `Makefile.in` using `sed`. If safe formatted-output APIs are unavailable, it adds fallback macros and prints warnings that builds may be vulnerable to string-format buffer overflow issues. The script is deliberately simple and not Autoconf-generated.

## Dependencies
Requires `/bin/sh`, `sed`, compiler/linker tools, `uname`, optional `nm`, and local `zlib.h`, `zconf.in.h`, and `Makefile.in`.

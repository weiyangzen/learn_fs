# sources/security-integrity/selinux/libselinux/src/libselinux.pc.in

Purpose: Template for the installed pkg-config metadata for libselinux.

Important APIs/types/functions: defines `prefix`, `exec_prefix`, `libdir`, `includedir`, package `Name`, `Description`, `Version`, project URL, private requirements, linker flags, and Cflags. Placeholders `@prefix@`, `@libdir@`, `@includedir@`, `@VERSION@`, and `@PCRE_MODULE@` are substituted by the makefile.

Control flow: no runtime logic. Makefile target `libselinux.pc` runs `sed` substitutions.

State and persistence: installed `.pc` file guides downstream builds.

Dependencies and integration: consumers use it via `pkg-config --cflags --libs libselinux`; `Requires.private` exposes static-link dependencies on libsepol and the regex module.

Risks and test signals: packaging tests should verify substituted paths, version, private requirements, and that shared vs static link consumers receive correct flags.

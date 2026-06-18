# File Research: sources/virtualization/libguestfs/daemon/Makefile.am

This is the Automake build manifest for `guestfsd`. It enumerates generated RPC files, daemon C sources, OCaml sources/interfaces, linker inputs, test binaries, and manpage generation.

Key points:
- `BUILT_SOURCES` and `generator_built` capture generated daemon dispatch/stub/action files and generated OCaml interfaces.
- `guestfsd_SOURCES` is the central C daemon source list, including every C file in this group.
- Links C with OCaml output object `camldaemon.o`, gnulib, protocol/utils libraries, and optional feature libraries such as ACL, cap, Augeas, hivex, SELinux, TSK, YARA, JSON-C, PCRE2, rpm.
- Builds OCaml daemon components via `OCAMLFIND ... -output-obj`.
- Defines `daemon_utils_tests`, linking selected C helpers with OCaml test objects and stubs.
- Generates `guestfsd.8` and website HTML from `guestfsd.pod`.

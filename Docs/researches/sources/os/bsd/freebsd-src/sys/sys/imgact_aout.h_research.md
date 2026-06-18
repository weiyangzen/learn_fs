# File Research: sources/os/bsd/freebsd-src/sys/sys/imgact_aout.h

Describes classic BSD `a.out` executable headers and helper macros. It handles both little-endian and network-order encodings of the combined magic/machine-id/flag field and defines magic constants for `OMAGIC`, `NMAGIC`, `ZMAGIC`, and `QMAGIC`.

Macros calculate text/data addresses, offsets, relocation table offsets, symbol table offsets, string table offsets, alignment, and bad-magic checks. `struct exec` is the on-disk header containing segment sizes, symbol sizes, entry point, and relocation sizes.

The kernel-only declaration exposes `aout_coredump()`, showing this header still supports legacy coredump/image-format paths.

# File Research: sources/virtualization/nbdkit/filters/qcow2dec/Makefile.am

This build file compiles the read-only qcow2 decoder filter from `qcow2dec.c` and `qcow2.h`. It includes core headers, replacements, and utilities, and adds zlib, zlib-ng, and libzstd compiler/linker flags when configured.

The module links utilities, replacements, platform import support, and compression libraries. It distributes and optionally generates the `nbdkit-qcow2dec-filter` manual, and uses standard filter module flags plus optional linker-script restriction.

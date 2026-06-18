# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsjconf.h

Ghostscript’s `jconfig.h` configuration wrapper for Independent JPEG Group code. It is intended to be combined with `stdpre.h` externally because of the IJG build directory layout, then includes `arch.h` for platform characteristics.

Defines IJG feature/configuration macros such as `HAVE_PROTOTYPES`, unsigned char/short support, optional standard headers under `__STDC__`, and disables BSD strings, sys/types, far pointers, short external names, and broken incomplete types.

Also adjusts `MAX_ALLOC_CHUNK` on small-int architectures and, for JPEG internals, sets `RIGHT_SHIFT_IS_UNSIGNED` based on `ARCH_ARITH_RSHIFT`. The file is a build-portability bridge rather than runtime logic.

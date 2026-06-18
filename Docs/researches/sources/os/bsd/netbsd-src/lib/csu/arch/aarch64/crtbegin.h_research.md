# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/aarch64/crtbegin.h

AArch64 declarations for constructor/destructor helper linkage. It marks `__do_global_ctors_aux` as a constructor and, for shared objects, marks `__do_global_dtors_aux` as a destructor.

This is used by the common C `crtbegin.c` path because the architecture uses init/fini arrays.

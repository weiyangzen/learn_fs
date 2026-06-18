# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/or1k/crtbegin.h

OR1K `crtbegin` header. It marks `__do_global_ctors_aux` as a constructor and, for shared builds, marks `__do_global_dtors_aux` as a destructor.

This matches the init/fini array startup path.

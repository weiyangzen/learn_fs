# File Research: sources/os/bsd/netbsd-src/lib/csu/common/crtbegin.c

Common C `crtbegin` implementation for architectures without architecture-specific `crtbegin.S`. It defines JCR and EH frame anchors, `__dso_handle`, weak references to Java and EH frame helper functions, and legacy ctor/dtor section anchors when init/fini arrays are unavailable.

`__do_global_ctors_aux` registers EH frames, registers Java classes if present, and runs constructors. `__do_global_dtors_aux` runs `__cxa_finalize` for shared objects, walks destructors, and deregisters EH frames. Both are guarded by one-time flags.

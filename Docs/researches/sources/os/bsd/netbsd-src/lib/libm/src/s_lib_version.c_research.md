# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_lib_version.c

Defines and initializes FDLIBM compatibility global `_LIB_VERSION`.

Key behavior: selects `_POSIX_`, `_XOPEN_`, `_SVID_`, or `_IEEE_` at compile time based on mode macros.

Important dependencies: `math.h` and `math_private.h`.

Notable risks: global behavior affects legacy wrapper error handling elsewhere in libm.

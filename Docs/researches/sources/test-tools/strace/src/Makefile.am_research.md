# sources/test-tools/strace/src/Makefile.am

Purpose: main Automake build description for the strace binary, static library, generated headers, ioctl tables, and mpers compatibility libraries.

Important APIs/types/functions: defines `bin_PROGRAMS=strace`, `libstrace.a`, include flags for build/source architecture directories and bundled headers, `libstrace_a_SOURCES`, optional stacktrace/SELinux source additions, `EXTRA_DIST`, `BUILT_SOURCES`, `CLEANFILES`, ioctl generation rules, `sys_func.h`, `sen.h`, and mpers printer/type/function generation rules.

Control flow: Automake builds `libstrace.a` from decoder/runtime sources, links `strace`, builds helper programs, generates syscall function prototypes by scanning `SYS_FUNC`, generates syscall entry names, builds ioctl sorter helpers from architecture ioctl includes, and preprocesses mpers sources to create native/m32/mx32 printer declarations/definitions and compatibility libraries when enabled.

State and persistence behavior: produces numerous generated headers and build artifacts in the build directory; distribution state is captured through the extensive `EXTRA_DIST` list of architecture-specific files and scripts.

Dependencies and integration points: central integration point for configure substitutions (`@arch@`, `@karch@`, feature flags, compiler flags), xlat `Makemodule.am`, `scno.am`, `mpers.am`, generated `maint/gen` outputs, and optional libraries libdw/libunwind/libiberty/libselinux.

Risks: high drift risk because source lists, generated headers, and `EXTRA_DIST` must be complete and ordered. Host/build/target distinction for ioctl and mpers rules is subtle. Generated files like `sys_func.h` must exist before preprocessing sources that include them.

Test signals: `autoreconf/bootstrap`, `configure`, `make`, `make distcheck`, feature-enabled builds, mpers builds, and cleanup/distclean targets are the primary validation gates.

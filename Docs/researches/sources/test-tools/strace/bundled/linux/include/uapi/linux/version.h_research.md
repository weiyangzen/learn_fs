# sources/test-tools/strace/bundled/linux/include/uapi/linux/version.h

Purpose: exposes the bundled Linux kernel version constants used by generated or vendored UAPI headers. It records a version code for Linux 7.1.0 and provides the standard `KERNEL_VERSION(a,b,c)` packing macro.

Important APIs/types/functions: `LINUX_VERSION_CODE` is `459008`, matching `KERNEL_VERSION(7,1,0)`. `KERNEL_VERSION(a,b,c)` shifts major by 16 bits, patchlevel by 8 bits, and clamps sublevel values above 255 to 255. The component macros are `LINUX_VERSION_MAJOR 7`, `LINUX_VERSION_PATCHLEVEL 1`, and `LINUX_VERSION_SUBLEVEL 0`.

Control flow: none at runtime. The macro is compile-time arithmetic used in preprocessor conditionals or C expressions that compare kernel header versions.

State/persistence behavior: no mutable state. The constants are a snapshot of the kernel UAPI version from which this bundled header set was generated.

Dependencies/integration: no includes. strace and its bundled-header generation logic can use these constants to gate version-specific decoders or to report the header baseline.

Risks and test signals: risks are stale version snapshots, incorrect clamping expectations for sublevels greater than 255, and mismatches between this bundled version and individual header content. Tests should verify `LINUX_VERSION_CODE == KERNEL_VERSION(7,1,0)`, major/patchlevel/sublevel parsing, and macro clamping behavior.

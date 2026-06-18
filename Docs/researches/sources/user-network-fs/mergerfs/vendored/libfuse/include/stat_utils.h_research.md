<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/stat_utils.h -->
# sources/user-network-fs/mergerfs/vendored/libfuse/include/stat_utils.h

Purpose: This platform shim exposes nanosecond timestamp access macros for `struct stat`.

Important APIs: on Linux, `ST_ATIM_NSEC`, `ST_CTIM_NSEC`, and `ST_MTIM_NSEC` read `st_atim.tv_nsec`, `st_ctim.tv_nsec`, and `st_mtim.tv_nsec`. On FreeBSD, they read the `st_*timespec.tv_nsec` fields. Other platforms produce a compile-time error.

State and integration: there is no state. Attribute conversion code uses these macros when populating FUSE timestamp fields.

Risks and test signals: unsupported platforms fail compilation, which is preferable to silently losing precision. Tests should compile on target platforms and verify nanosecond values round-trip in getattr/statx replies.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/stat_utils.h -->

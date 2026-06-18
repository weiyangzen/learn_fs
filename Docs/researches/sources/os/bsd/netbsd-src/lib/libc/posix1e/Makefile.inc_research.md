# File Research: sources/os/bsd/netbsd-src/lib/libc/posix1e/Makefile.inc

Build include for POSIX.1e and NFSv4 ACL libc support. It adds `posix1e` and `sys/kern` to `.PATH`, defines `_ACL_PRIVATE`, and builds ACL object manipulation, parsing, text conversion, validation, kernel syscall wrappers, and NFSv4 support files.

It also installs ACL, extended attribute, and POSIX.1e manual pages with many MLINK aliases for public API variants.

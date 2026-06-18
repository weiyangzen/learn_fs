# sources/test-tools/strace/bundled/linux/include/uapi/linux/libc-compat.h

Purpose: coordinates Linux UAPI headers with libc headers to avoid duplicate struct, macro, and enum definitions while preserving ABI-compatible layouts.

Important APIs/types/functions: the exported surface is a set of `__UAPI_DEF_*` guard macros for net interface, IPv4/IPv6 socket structures/options, and xattr definitions. The logic branches on glibc markers such as `__GLIBC__`, `_NET_IF_H`, `_NETINET_IN_H`, `_SYS_XATTR_H`, and feature macros.

Control flow: UAPI headers include this early, then wrap conflicting definitions in `#if __UAPI_DEF_FOO`. If libc headers were included first, the UAPI header suppresses duplicates; if Linux headers come first, the guards tell libc to suppress duplicates later.

State/persistence behavior: compile-time only; no runtime state. The "state" is preprocessor include order and feature macro visibility in the translation unit.

Dependencies/integration: integrates with glibc and other libc implementations that may predefine `__UAPI_DEF_*`. It is foundational for headers such as networking ABI files included alongside libc headers.

Risks and test signals: risks are include-order regressions and unsupported libc behavior. Tests should compile small C snippets with libc-first and Linux-first include ordering for `net/if.h`, `netinet/in.h`, and `sys/xattr.h`.

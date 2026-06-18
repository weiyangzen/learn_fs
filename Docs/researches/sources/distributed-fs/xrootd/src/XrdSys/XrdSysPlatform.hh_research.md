## sources/distributed-fs/xrootd/src/XrdSys/XrdSysPlatform.hh

Purpose: central platform portability header for constants, byte swapping, networking types, filesystem macros, and utility declarations.

Important APIs/types/functions: platform definitions for `MAXNAMELEN`, `MAXPATHLEN`, `fdatasync`, `off64_t`, `STATFS`, `FS_BLKFACT`, `FLOCK_t`, `SHMDT_t`, endian macros/conversions `htonll`, `ntohll`, `h2nll`, `n2hll`, `bswap()` overloads, `SOCKLEN_t`, `PTR2INT`, `Netdata_t`, `Sokdata_t`, `IOV_INIT`, `MAKEDIR`, `CHMOD`, `net_errno`, `LT_MODULE_EXT`, and `XrdSys::getIovMax()`.

Control flow: large preprocessor matrix selects behavior for Linux, Apple, FreeBSD, GNU/Hurd, Solaris, AIX, and Windows. Endianness detection either defines pass-through conversions, byte-swap conversions, or errors out on unknown non-Windows targets.

State and persistence: no runtime state in the header. It defines compile-time contracts consumed across XrdSys.

Dependencies and integration: includes C standard integer/stdlib headers and platform headers such as byteswap, OSByteOrder, sys/param, and Windows compatibility. Nearly all low-level XRootD utility code can depend on it.

Risks: macro-heavy portability code can collide with system headers or caller identifiers. Hardcoded GNU/Hurd path/name limits are acknowledged as imperfect. `PTR2INT` truncates pointers by design. Unknown endianness is a hard compile failure.

Test signals: platform matrix builds, endian conversion tests, socket type compatibility, filesystem macro use, `LT_MODULE_EXT` override, and inclusion-order tests with system headers.

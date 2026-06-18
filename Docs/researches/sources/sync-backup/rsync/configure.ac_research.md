# sources/sync-backup/rsync/configure.ac

## Purpose
Autoconf source for rsync's platform and dependency configuration. It discovers compiler features, headers, system calls, libraries, optional compression/checksum/auth features, ACL/xattr/iconv support, daemon defaults, generated build substitutions, and portability replacement functions.

## Important APIs, Types, and Functions
Defines package/config headers, substitutes build variables such as `BUILD_POPT`, `BUILD_ZLIB`, `ROLL_SIMD`, `ROLL_ASM`, `MD5_ASM`, `MAKE_MAN`, `MAKE_RRSYNC`, object-save flags, and generated files (`Makefile`, `lib/dummy`, `zlib/dummy`, `popt/dummy`, `shconfig`). Feature macros include `HAVE_OPENAT2`, `USE_OPENSSL`, `SUPPORT_XXHASH`, `SUPPORT_ZSTD`, `SUPPORT_LZ4`, `SUPPORT_ACLS`, `SUPPORT_XATTRS`, `ICONV_OPTION`, `USE_ICONV_OPEN`, `INET6`, `HAVE_SOCKETPAIR`, `HAVE_SECURE_MKSTEMP`, and many platform probes.

## Control Flow
The script initializes Autoconf, reads `RSYNC_VERSION`, configures debug/profile/coverage/openat2/md2man/maintainer flags, selects default paths (`RSYNC_PATH`, `RSYNCD_SYSCONF`, `RSYNC_RSH`, nobody user/group), probes SIMD and assembler optimizations, handles zlib/popt inclusion, checks crypto/checksum/compression libraries, aborts if required optional-default libraries are missing, probes types/functions/network portability, configures iconv, filesystem semantics, socketpair, ACLs, xattrs, compiler object behavior, and finally emits configured files.

## State and Persistence Behavior
Generates the Autoconf output that produces `config.h`, `Makefile`, `shconfig`, and dummy dependency markers. It records platform choices in preprocessor macros and make substitutions that change compiled runtime behavior, including security-sensitive secure-open and xattr/ACL paths.

## Dependencies and Integration Points
Depends on Autoconf 2.69+, C/C++ compilers, awk/egrep/install/mkdir, optional Perl/Python3, md2man, OpenSSL, xxhash, zstd, lz4, zlib, popt, ACL/xattr system libraries, and platform headers/syscalls. It integrates with almost every C file through `config.h`.

## Risks and Test Signals
Risks include wrong cross-compilation defaults, feature macros enabled without linkable functions, optional dependency failures blocking default builds, insecure fallback selection for openat2/secure mkstemp, and platform-specific ACL/xattr misclassification. Test signals include `autoreconf`/`prepare-source`, clean `./configure`, configured builds with `--disable-*` options, coverage builds, cross-compile cache overrides, Linux and non-Linux hosts, bundled/external zlib and popt, and feature-specific tests for iconv, xattrs, ACLs, openat2 fallback, SIMD, and compression libraries.

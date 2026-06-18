
# sources/security-integrity/keyutils/Makefile

## Purpose
The keyutils top-level `Makefile` builds the keyutils library, command-line tools, DNS resolver helper, C++ header syntax check, install targets, tests, cleanup, tarball generation, and RPM packaging.

## Important APIs, Types, And Functions
Major variables include `VERSION`, `APIVERSION`, `ARLIB`, `DEVELLIB`, `SONAME`, `LIBNAME`, `LIBDIR`, `USRLIBDIR`, `NO_ARLIB`, `NO_SOLIB`, and `NO_GLIBC_KEYERR`. Targets build `libkeyutils.a`, `libkeyutils.so.*`, `keyctl`, `request-key`, `key.dns_resolver`, `cxx.stamp`, install artifacts, tests, tarballs, SRPM/RPMs, and `show_vars`.

## Control Flow
Version data is derived from `keyutils.spec` and `version.lds`. Architecture/libdir defaults are inferred from system binaries. Conditional blocks build static/shared libraries unless disabled. Programs link against the locally built library. Install targets copy binaries, libraries, config, pkg-config data, headers, man pages, and symlinks into `DESTDIR` paths.

## State And Persistence
Build artifacts include libraries, object files, binaries, pkg-config files, symlinks, tarballs, and RPM build directories. Install mutates the destination filesystem with keyutils tools and configuration.

## Dependencies And Integration Points
It depends on GCC/G++, binutils, Make, sed, grep, ldd, file, rpmspec/rpmbuild for packaging, `libresolv` for `key.dns_resolver`, and the local version script. It installs `/sbin/key.dns_resolver` and request-key configuration used by kernel key request callouts.

## Risks
Libdir and word-size inference are host-specific. `CFLAGS :=` at the top can override environment expectations unless passed by make origin logic later. Install symlinks are absolute-ish through `$(LIBDIR)` and `$(USRLIBDIR)` choices, so packaging paths need review.

## Test Signals
`make test` delegates to `tests run`; `cxx.stamp` checks public header C++ syntax; `-Wall -Werror` makes compiler warnings fail the build.

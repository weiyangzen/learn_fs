# sources/test-tools/strace/configure.ac

## Purpose
Defines strace's Autoconf/Automake configuration logic. It establishes package metadata, supported architectures and personalities, bundled-header selection, compiler/build tools, feature probes, libc/kernel compatibility shims, optional stacktrace/SELinux/coverage/valgrind/install-test features, mpers support, generated outputs, and substitution variables consumed by the build and packaging system.

## Important APIs, Types, and Functions
Read coverage: 827 lines and 22534 bytes. Top-level macros include `AC_PREREQ`, `AC_INIT`, `AC_CONFIG_SRCDIR`, `AC_CONFIG_AUX_DIR`, `AC_CONFIG_HEADERS`, `AM_INIT_AUTOMAKE`, `AM_MAINTAINER_MODE`, `AC_CANONICAL_HOST`, compiler/tool probes, `AC_USE_SYSTEM_EXTENSIONS`, and `AX_CODE_COVERAGE`. It computes version, copyright year, manpage dates, and bundled Linux version through build-aux scripts and substitutes `RPM_CHANGELOGTIME`, `DEB_CHANGELOGTIME`, `COPYRIGHT_YEAR`, `STRACE_MANPAGE_DATE`, and `SLM_MANPAGE_DATE`.

The architecture case maps host CPUs to strace `arch`, kernel `karch`, m32/mx32 personalities, compiler flags, and `AC_DEFINE`s for AARCH64, ALPHA, ARC, ARM, HPPA, I386, LOONGARCH64, MIPS, POWERPC variants, RISCV64, S390X, SPARC, X32, X86_64, and others. Options include `--enable-bundled`, `--enable-arm-oabi`, `--enable-mpers`, and `--enable-install-tests`. Feature probes cover functions, types, headers, struct members, declarations, sizes, signal constants, builtins, library search results for dl/rt/m/termcap, readelf, stacktrace, SELinux, valgrind, and many Linux header structures used by decoders.

## Control Flow
Configure first initializes package metadata and tools, then determines endian and architecture. It validates supported host CPU, sets architecture variables and defaults, decides whether bundled kernel headers are needed by comparing system `<linux/version.h>` against the bundled version, and amends `CPPFLAGS` if bundled headers are selected. MIPS ABI and ARM OABI options are resolved next. The script then probes C functions, types, members, headers, and declarations, creating fallback generated headers for missing `struct sockaddr_storage` or incompatible `<linux/signal.h>` combinations.

Later flow computes ABI sizes and signal constants, probes compiler/library features, runs project-specific macros such as `st_CHECK_ENUMS`, `st_STACKTRACE`, and `st_SELINUX`, generates MIPS syscallent stubs when needed, discovers aarch64 compat compilers, sets default m32/mx32 compiler variables, invokes `st_MPERS` for supported secondary personalities, configures optional installed tests and valgrind defaults, declares generated files, and emits `AC_OUTPUT`.

## State and Persistence Behavior
Configure writes `src/config.h`, generated Makefiles, `debian/changelog`, `doc/strace.1`, `doc/strace-log-merge.1`, `strace.spec`, cache variables, and in some compatibility paths generated headers or MIPS syscall stubs under the build tree. It persists selected architecture, feature availability, library flags, header choices, mpers settings, and manpage/package substitutions into generated build artifacts rather than runtime state.

## Dependencies and Integration Points
Depends on Autoconf, Automake, project m4 macros, build-aux scripts, C compiler/preprocessor/linker, system and bundled Linux headers, optional cross compilers, optional libraries (`dl`, `rt`, `m`, termcap/ncurses/tinfo, stacktrace providers, SELinux), and valgrind/code coverage macros. It integrates with `ci/run-build-and-tests.sh`, `debian/rules`, bundled Linux UAPI headers, `src/config.h` conditional compilation, generated syscall tables, manpage templates including `strace-log-merge.1.in`, RPM/Debian packaging, tests and tests-m32/tests-mx32 directories.

## Risks and Edge Cases
Architecture detection is central; wrong `arch`/`karch` mapping affects syscall tables and bundled include paths. Bundled-header selection compares only version granularity and can differ from vendor-patched system headers. Probes that temporarily modify `CPPFLAGS` must restore it correctly. Missing or incompatible Linux/libc headers trigger fallback copies that can shadow system headers. Cross and mpers builds depend on compiler availability and ABI flags. Generated MIPS stubs can fail when `no_create` is not set. Library probes save/restore `LIBS` to avoid contaminating later checks. Cache variables supplied by CI can force paths that need validation.

## Test Signals
Run `./bootstrap && ./configure` across supported native and cross-like targets, with `--enable-bundled=yes/no/check`, `--enable-mpers` variants, `--enable-arm-oabi`, stacktrace backends, SELinux present/absent, coverage, valgrind, install-tests, and old/new kernel headers. Verify generated `src/config.h`, architecture substitutions, Makefile conditionals, bundled include flags, MIPS stubs, manpage date substitutions, Debian changelog substitution, and full `make distcheck` plus mpers tests.

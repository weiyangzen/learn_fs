# sources/security-integrity/audit-userspace/auparse/Makefile.am

Purpose: Defines the build graph for `libauparse`, its generated interpretation tables, pkg-config metadata, and auparse tests.

Important APIs, types, and functions: Declares `lib_LTLIBRARIES = libauparse.la`, installs `auparse.h` and `auparse-defs.h`, and sets `pkgconfig_DATA = auparse.pc`. `libauparse_la_SOURCES` includes core parser files (`auparse.c`, `ellist.c`, `nvlist.c`, `interpret.c`, `expression.c`, `auditd-config.c`, `data_buf.c`, normalization files, and headers). `BUILT_SOURCES` and `noinst_PROGRAMS` define many generated lookup-table headers and generator binaries.

Control flow: Automake builds generator programs from `../lib/gen_tables*.c` with `CC_FOR_BUILD`, then runs them with options such as `--i2s`, `--s2i`, `--i2s-transtab`, and `--64bit` to generate headers like `accesstabs.h`, `captabs.h`, `clone-flagtabs.h`, `bpftabs.h`, and normalization maps. `message.c` is copied from `lib/message.c`. The library links against `libaudit.la` and `libaucommon.la` and uses relro linker flags.

State and persistence: Build artifacts include generated headers, copied `message.c`, libtool objects, and installed pkg-config file. `CLEANFILES`, `CONFIG_CLEAN_FILES`, and `DISTCLEANFILES` define cleanup behavior.

Dependencies and integration points: Integrates auparse with the top-level libaudit/common libraries, generated kernel constant translation tables, normalization maps, and the `auparse/test` subdirectory. The small table headers in this subset are data inputs to this file's generator rules.

Risks and edge cases: The generated headers depend on build-host tools and `CC_FOR_BUILD`, so cross-build correctness matters. Many rules use source headers as compile-time macro includes; stale generated headers can misrepresent kernel constants. The file is long and repetitive, making copy/paste naming errors possible between generator target names and output header names.

Test signals: The `SUBDIRS = . test` path includes auparse tests after building the library. Successful `make check` here signals both generated table availability and core library linkability, but functional parser behavior is mostly covered in `auparse/test`, not in this Makefile itself.

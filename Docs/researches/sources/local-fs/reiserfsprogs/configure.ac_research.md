# File Research: sources/local-fs/reiserfsprogs/configure.ac

Autoconf configuration for `reiserfsprogs` version `3.6.27`. It initializes Automake/libtool, config header generation, compiler checks, large-file support, required libraries, warning flags, and output Makefiles/manpage substitutions.

Important checks:
- Requires `libcom_err`; warns if `libuuid` is absent.
- Requires either `register_printf_modifier` or `register_printf_specifier`.
- Forces `_FILE_OFFSET_BITS=64` when large-file detection is inconclusive.
- Checks `off_t` and `blkcnt_t` sizes.
- Adds `-I$(top_srcdir)/include` to `CPPFLAGS`.

Build outputs include all major tool subdirectories: `mkreiserfs`, `resize_reiserfs`, `fsck`, `lib`, root `Makefile`, `reiserfscore`, `debugreiserfs`, and `tune`.

Notable option: `--enable-io-failure-emulation` defines `IO_FAILURE_EMULATION`, but the configure text warns it is debugging-only.

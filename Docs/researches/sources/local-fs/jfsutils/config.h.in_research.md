# File Research: sources/local-fs/jfsutils/config.h.in

This is the Autoheader-generated template for `config.h`. It lists all preprocessor symbols that `configure` may define or leave undefined.

Primary contents:
- Header availability macros for endian, mount, stat, sysmacros, UUID, standard C, and platform-specific headers.
- Function availability macros for `fseeko`, `getcwd`, `getmntinfo`, `memalign`, `posix_memalign`, `strtol`, and `strtoul`.
- Type/structure macros for `struct stat.st_rdev`, `mode_t`, `off_t`, `size_t`, `const`, and `inline`.
- Large-file support macros: `_FILE_OFFSET_BITS`, `_LARGEFILE_SOURCE`, `_LARGE_FILES`.
- Package metadata macros: `PACKAGE`, `PACKAGE_*`, and `VERSION`.

Important integration points:
- Generated from `configure.in` by `autoheader`.
- Consumed by `configure`/`config.status` to produce `config.h`.
- Acts as the contract between Autoconf feature probes and conditional C compilation in the jfsutils source tree.

Portability/build observations:
- The template intentionally uses `#undef` for every configurable feature.
- It should be regenerated after changing checks in `configure.in`.
- It is portable input, while `config.h` is configured output.

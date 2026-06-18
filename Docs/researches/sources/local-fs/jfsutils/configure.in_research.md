# File Research: sources/local-fs/jfsutils/configure.in

This is the handwritten Autoconf input that defines jfsutils configuration behavior.

Primary behavior:
- Sets `AC_INIT(libfs/super.c)`, making `libfs/super.c` the source-presence sentinel.
- Declares package/version with `AM_INIT_AUTOMAKE(jfsutils, 1.1.15)`.
- Generates `config.h` via `AM_CONFIG_HEADER(config.h)`.
- Disables maintainer rules by default with `AM_MAINTAINER_MODE`.
- Checks required programs: `awk`, C compiler, install tool, `ln`, symbolic links, and `ranlib`.
- Checks portability headers and requires `uuid/uuid.h`.
- Checks C language/types/structures: `const`, `inline`, `mode_t`, `off_t`, `size_t`, `struct stat.st_rdev`, and `struct tm`.
- Checks functions: `memcmp`, `getcwd`, `getmntinfo`, `strtol`, `strtoul`, `posix_memalign`, `memalign`.
- Enables large-file and `fseeko` checks.
- Adds warning flags for GCC.
- Defaults installation to `/usr` and system utilities to `/sbin` when no prefix is supplied.
- Emits Makefiles for every top-level build component plus `jfsutils.spec`.

Important integration points:
- The required UUID header links jfsutils to the libuuid/e2fsprogs development ecosystem.
- The subdirectory outputs match the top-level `Makefile.am` recursive list.
- The `/sbin` default is significant because tools like `fsck.jfs` and `mkfs.jfs` are administrative filesystem utilities.

Portability/build observations:
- This file is the correct place to change configuration checks.
- The generated `configure` currently reflects this file through Autoconf 2.65-era output.
- It uses the older `configure.in` naming convention rather than modern `configure.ac`.

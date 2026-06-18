# File Research: sources/local-fs/jfsutils/configure

This is the generated GNU Autoconf 2.65 `configure` script for jfsutils. It is generated from `configure.in` and adapts the build to the host/toolchain.

Primary behavior:
- Parses standard configure options such as `--prefix`, `--sbindir`, `--host`, `--build`, `--enable-maintainer-mode`, `--disable-dependency-tracking`, and `--disable-largefile`.
- Locates source root by requiring `libfs/super.c`.
- Initializes package identity as `jfsutils` version `1.1.15`.
- Finds required build tools: install program, `mkdir -p`, `awk`, C compiler, preprocessor, `grep`, `egrep`, `ln`, `ln -s`, `ranlib`, `strip`, and Automake helper tools.
- Sets up Automake dependency tracking and chooses compiler dependency mode via `depcomp`.
- Creates `config.status`, `config.h`, all top-level/subdirectory Makefiles, and `jfsutils.spec`.

Project-specific checks:
- Standard C headers through `AC_HEADER_STDC`.
- Headers: `endian.h`, `fcntl.h`, `mntent.h`, `unistd.h`, `stdbool.h`, `stdint.h`, `machine/endian.h`, `sys/byteorder.h`, `sys/mount.h`, `sys/param.h`, `sys/statvfs.h`, `sys/sysmacros.h`, `sys/disklabel.h`.
- Required UUID header: `uuid/uuid.h`; failure stops configuration with an instruction to install e2fsprogs/libuuid development headers.
- C characteristics/types: `const`, `inline`, `mode_t`, `off_t`, `size_t`, `struct stat.st_rdev`, and `struct tm` location.
- Functions: working `memcmp`, `getcwd`, `getmntinfo`, `strtol`, `strtoul`, `posix_memalign`, `memalign`.
- Large-file support through `AC_SYS_LARGEFILE` and `AC_FUNC_FSEEKO`.

Generated outputs:
- `Makefile`
- `libfs/Makefile`
- `include/Makefile`
- `fsck/Makefile`
- `fscklog/Makefile`
- `logdump/Makefile`
- `mkfs/Makefile`
- `tune/Makefile`
- `xpeek/Makefile`
- `jfsutils.spec`
- `config.h`
- dependency placeholder files under `.deps` where needed.

Important integration points:
- If `CC` is exactly `gcc`, `AM_CFLAGS` becomes `-Wall -Wstrict-prototypes -fno-strict-aliasing`.
- Default prefix is `/usr`.
- If neither `prefix` nor `exec_prefix` is supplied, `sbindir` is forced to `/sbin`, matching filesystem administration tool conventions.
- Maintainer-mode regeneration rules are disabled by default.
- `config.status` embeds the substitutions used by `Makefile.in` and other templates.

Portability/build observations:
- The script supports cross-compilation option handling, but some runtime tests, such as working `memcmp`, degrade under cross-compilation.
- It is generated and should not be manually edited for durable changes.
- The source of truth is `configure.in`; after edits, `autoconf`/`autoheader`/`automake` should regenerate this script and templates.
- The script is old Autoconf-era shell, but still largely conventional for legacy C utilities.

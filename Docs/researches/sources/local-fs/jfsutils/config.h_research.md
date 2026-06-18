# File Research: sources/local-fs/jfsutils/config.h

This is the configured Autoconf header generated from `config.h.in` by `configure`. It captures the feature set detected for the environment where jfsutils was configured.

Enabled platform features:
- Headers: `endian.h`, `fcntl.h`, `inttypes.h`, `memory.h`, `mntent.h`, `stdbool.h`, `stdint.h`, `stdlib.h`, `strings.h`, `string.h`, `sys/mount.h`, `sys/param.h`, `sys/statvfs.h`, `sys/stat.h`, `sys/sysmacros.h`, `sys/types.h`, `unistd.h`, `uuid/uuid.h`.
- Functions: `fseeko`, `getcwd`, `memalign`, `posix_memalign`, `strtol`, `strtoul`.
- Types/structs: ANSI C headers are available, `struct stat` has `st_rdev`.
- Package identity: `PACKAGE` is `jfsutils`; `VERSION` is `1.1.15`.

Disabled or unavailable features in this configured environment:
- `getmntinfo`
- `machine/endian.h`
- `sys/byteorder.h`
- `sys/disklabel.h`
- `TM_IN_SYS_TIME`
- `_FILE_OFFSET_BITS`
- `_LARGEFILE_SOURCE`
- `_LARGE_FILES`
- fallback replacements for `const`, `inline`, `mode_t`, `off_t`, and `size_t`.

Important integration points:
- Source files include this header through `-DHAVE_CONFIG_H`.
- The JFS utility code can use these macros to select Linux/glibc-style headers and allocation APIs.
- `HAVE_UUID_UUID_H` indicates the build depends on libuuid/e2fsprogs-style UUID headers being present.

Portability/build observations:
- This file is environment-specific generated output, not a portable source template.
- Its current values reflect one configuration run and may not match another host or cross-toolchain.
- Because `_FILE_OFFSET_BITS` is undefined here, the configured environment already had suitable large-file behavior without needing that macro.

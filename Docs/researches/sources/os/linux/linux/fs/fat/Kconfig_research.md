# File Research: sources/os/linux/linux/fs/fat/Kconfig

Defines Kconfig options for Linux FAT-family filesystem support.

Key behavior:
- `FAT_FS` is the shared base tristate for FAT-family filesystems.
  - Selects `BUFFER_HEAD`, `NLS`, and `LEGACY_DIRECT_IO`.
  - Provides common FAT support but is not directly sufficient for mounting unless `MSDOS_FS` or `VFAT_FS` is enabled.
  - Builds as module `fat` when modular.
- `MSDOS_FS` enables classic MS-DOS FAT filesystem support.
  - Selects `FAT_FS`.
  - Builds as module `msdos` when modular.
  - Documentation notes that Windows long filenames require VFAT instead.
- `VFAT_FS` enables FAT support with Windows long filenames.
  - Selects `FAT_FS`.
  - Builds as module `vfat` when modular.
  - Points users to `Documentation/filesystems/vfat.rst`.
- `FAT_DEFAULT_CODEPAGE` sets the default FAT codepage.
  - Depends on `FAT_FS`.
  - Defaults to `437`.
  - Can be overridden by the `codepage` mount option.
- `FAT_DEFAULT_IOCHARSET` sets the default VFAT input/output charset.
  - Depends on `VFAT_FS`.
  - Defaults to `iso8859-1`.
  - Can be overridden by the `iocharset` mount option.
  - Explicitly discourages setting this to `utf8` directly.
- `FAT_DEFAULT_UTF8` controls whether the FAT `utf8` mount option is enabled by default.
  - Depends on `VFAT_FS`.
  - Defaults to `n`.
  - Can be overridden per mount with `utf8=0`.
- `FAT_KUNIT_TEST` builds FAT KUnit tests.
  - Depends on `KUNIT && FAT_FS`.
  - Defaults to `KUNIT_ALL_TESTS`.
  - Builds FAT filesystem unit tests when enabled.

Important interactions:
- The Makefile uses these config symbols to include `fat.o`, `vfat.o`, `msdos.o`, and `fat_test.o`.
- FAT charset/codepage defaults are runtime mount-option defaults consumed by FAT/VFAT implementation files outside this group.

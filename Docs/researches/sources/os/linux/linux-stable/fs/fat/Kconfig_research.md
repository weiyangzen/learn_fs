# File Research: sources/os/linux/linux-stable/fs/fat/Kconfig

## Purpose
`Kconfig` defines Linux kernel configuration options for FAT-family filesystem support.

## Main Options
- `FAT_FS`: common FAT foundation layer. It is tristate, selects `BUFFER_HEAD`, `NLS`, and `LEGACY_DIRECT_IO`, and is required by MSDOS and VFAT.
- `MSDOS_FS`: enables classic MSDOS FAT filesystem support and selects `FAT_FS`.
- `VFAT_FS`: enables VFAT/Windows long filename support and selects `FAT_FS`.
- `FAT_DEFAULT_CODEPAGE`: integer default FAT codepage, dependent on `FAT_FS`, default `437`.
- `FAT_DEFAULT_IOCHARSET`: default VFAT charset string, dependent on `VFAT_FS`, default `"iso8859-1"`.
- `FAT_DEFAULT_UTF8`: boolean to enable the FAT `utf8` mount option by default, dependent on `VFAT_FS`, default `n`.
- `FAT_KUNIT_TEST`: tristate KUnit tests for FAT, dependent on `KUNIT && FAT_FS`, defaulting to `KUNIT_ALL_TESTS`.

## Behavior and Dependencies
The configuration separates the shared FAT core from the two mountable frontends. The help text explains that `FAT_FS` alone is just the shared foundation, while `MSDOS_FS` and/or `VFAT_FS` provide usable filesystem support. Charset/codepage options define defaults that can still be overridden at mount time.

## Notable Edge Cases
- If FAT core is built as a module, dependent FAT-family filesystems must also be modules.
- The config text discourages using UTF-8 as the default FAT charset unless explicitly desired.

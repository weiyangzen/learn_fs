# File Research: sources/os/linux/linux/fs/efivarfs/Kconfig

Defines the `EFIVAR_FS` build option.

Key behavior:
- Adds tristate “EFI Variable filesystem” support.
- Depends on `EFI`.
- Defaults to module build.
- Describes efivarfs as the replacement for sysfs EFI variable access without the old 1024-byte size limit.

Important interactions:
- The built module is named `efivarfs`.

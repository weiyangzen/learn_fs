# File Research: sources/os/linux/linux-stable/fs/efivarfs/Kconfig

## Summary
Declares the EFI variable filesystem configuration option.

## Main Contents
- `CONFIG_EFIVAR_FS`
- Depends on `EFI`
- Defaults to module build
- Module name is `efivarfs`

## Important Behavior
The help text positions efivarfs as the replacement for old EFI variable sysfs support because it avoids the old 1024-byte variable size limit.

## Risks
None in code logic; enabling this exposes firmware variables through a filesystem interface, with safety handled by the implementation files.

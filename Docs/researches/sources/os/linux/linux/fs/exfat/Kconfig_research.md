# File Research: sources/os/linux/linux/fs/exfat/Kconfig

## Purpose
Defines kernel configuration entries for the exFAT filesystem driver.

## Main Interfaces
- `EXFAT_FS`: tristate option enabling built-in or module support for exFAT.
- `EXFAT_DEFAULT_IOCHARSET`: default charset used for converting between user-visible filenames and exFAT UTF-16 names.

## Dependencies
Selecting `EXFAT_FS` pulls in `BUFFER_HEAD`, `NLS`, and `LEGACY_DIRECT_IO`, matching the implementation’s use of buffer heads, kernel NLS tables, and legacy direct I/O paths.

## Behavior Notes
The help text identifies exFAT as common for SD cards and USB storage. If built as a module, the module name is `exfat`. The default iocharset is `utf8`, but mounts can override it with the `iocharset` option.

## Risks
Configuration directly controls availability of the full `fs/exfat` object set. Charset defaults affect filename interpretation and compatibility, especially when users do not provide an explicit mount option.

# File Research: sources/os/plan9/plan9/sys/src/9/port/mkdevlist

Purpose: rc/awk helper that emits object-file names needed by a kernel config.

Key logic:
- Parses `dev`, `misc`, `link`, and `ip` sections.
- Emits device object names as `dev<name>.$O`; other listed object names as `<name>.$O`.
- Includes extra object dependencies from additional fields unless marked with `+`, `=`, or `-` prefixes.
- Adds `bios32.$O` for 386 when `pci.$O` is present.

Dependencies and integration:
- Uses `$objtype` and config section conventions.

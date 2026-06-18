# File Research: sources/os/bsd/freebsd-src/sbin/mount_cd9660/mount_cd9660.c

## Summary
Mount helper for ISO 9660/CD9660 filesystems with Rock Ridge, Joliet, generation-number, permission mapping, session selection, and charset conversion options.

## Main Responsibilities
- Parses cd9660-specific options and standard/update mount options.
- Resolves uid/gid and masks from names or octal strings.
- Optionally reads CD-ROM TOC to choose the last data track starting sector.
- Forces read-only mount.
- Builds `nmount()` iovecs for `fstype=cd9660`, mount path, source device, start sector, and options.
- Loads `cd9660_iconv` and registers Unicode-to-local charset conversion for `-C`.

## Key Functions
- `get_ssector()`: reads CD TOC and returns last data track LBA.
- `set_charset()`: loads iconv module and builds charset iovecs.
- `a_uid()`, `a_gid()`, `a_mask()`: parse ownership/mode options.

## Research Notes
If no session is specified and TOC probing fails, the helper falls back to sector 0, preserving historical behavior.

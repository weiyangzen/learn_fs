# File Research: sources/windows/winfsp/src/sys/driver.inf.in

Purpose:
Template INF file for installing the WinFsp kernel driver package.

Contents:
- `[Version]` declares Windows NT signature, `Volume` setup class, volume class GUID `{71a27cdd-812a-11d0-bec7-08002be2092f}`, `PnpLockdown = 1`, and template placeholders for catalog file and provider.
- `[DestinationDirs]` sets the default destination directory to `12`, the system drivers directory.
- `[DefaultInstall.!ArchDecoration!]` installs by copying files from `Driver.CopyFiles`.
- `[Driver.CopyFiles]`, `[SourceDisksFiles]`, and `[SourceDisksNames]` are parameterized by `!DriverFile!` and identify the driver binary as coming from disk `1 = Disk1`.

Dependencies:
- Build or packaging scripts must substitute `!CatalogFile!`, `!Provider!`, `!ArchDecoration!`, and `!DriverFile!`.
- The resulting INF participates in Windows driver installation/signing flow rather than runtime driver logic.

Research notes:
- The template is intentionally minimal and copy-install oriented.
- Runtime behavior is determined by the driver binary and service configuration; this file mainly captures installation metadata.

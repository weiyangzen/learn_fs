# File Research: sources/os/bsd/freebsd-src/sbin/sysctl/sysctl.c

## Purpose
Main implementation of the FreeBSD `sysctl` userland utility. It parses command-line and file-based sysctl requests, resolves sysctl names to MIB OIDs, prints values and metadata, and sets writable leaf nodes.

## Main Elements
- `main()` handles display, assignment, all-node traversal, jail attachment, configuration file input, and filters for writable, tunable, prison, and vnet sysctls.
- `parse()` splits `name=value` or `name:value`, trims whitespace/quotes, validates leaf/writable status, parses numeric vectors or strings, performs `sysctl(3)`, and prints old/new values.
- `parsefile()` reads sysctl configuration files, strips comments outside quotes, trims whitespace, and feeds non-empty lines to `parse()`.
- `sysctl_all()` walks the sysctl tree using `CTL_SYSCTL_NEXT` or `CTL_SYSCTL_NEXTNOSKIP`.
- `show_var()` fetches name, format, type, and value, applies filters, and formats scalar, string, known opaque, raw, and hex output.
- Opaque structure printers cover `clockinfo`, `loadavg`, `timeval`, `vmtotal`, evdev `input_id`, page sizes, EFI maps, and BIOS SMAP xattrs.
- `strIKtoi()` parses temperature sysctl assignments with Celsius, Fahrenheit, Kelvin, or raw integer units for `IK` formats.
- Optional jail support attaches to a named jail before reads/writes.

## Dependencies And Integration
Uses FreeBSD sysctl metadata interfaces (`CTL_SYSCTL_NAME2OID`, `OIDFMT`, `NAME`, `OIDDESCR`, `NEXT/NEXTNOSKIP`), optional jail APIs, architecture-specific EFI/BIOS structures, evdev input IDs, and libc formatting/parsing.

## Risk Notes
Assignment paths must match kernel-reported type and size precisely. Tree walking intentionally skips `CTLFLAG_SKIP` descendants for ordinary `-a`, but metadata modes override that. File parsing is quote-aware but still line-oriented, so malformed quoted values can affect comment stripping.

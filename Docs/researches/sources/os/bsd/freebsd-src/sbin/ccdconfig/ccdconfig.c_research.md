# File Research: sources/os/bsd/freebsd-src/sbin/ccdconfig/ccdconfig.c

## Purpose
Configures, unconfigures, and dumps FreeBSD concatenated disk (`ccd`) GEOM devices.

## Main Elements
- CLI actions: configure one, configure all from a file, unconfigure one, unconfigure all, and dump configuration.
- `do_single()`: validates ccd name, interleave, flags, and providers; sends GEOM `create geom` or `destroy geom` requests.
- `do_all()`: reads `/etc/ccd.conf` or `-f` file, tokenizes non-comment lines, and applies configure/unconfigure action.
- `dumpout()` / `dump_ccd()`: request CCD class `list` output through GEOM control.
- `flags_to_val()`: parses numeric or comma-separated string flags.

## Dependencies And Integration
Uses kernel module loading (`modfind`, `kldload`) to try `geom_ccd`, and `libgeom` control APIs for runtime operations. `pathnames.h` supplies default config path.

## Risk Notes
This utility performs direct storage-topology mutation. Numeric flag parsing only allows a subset of flags in numeric form, while string parsing allows all declared flags.

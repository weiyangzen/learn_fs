# File Research: sources/os/bsd/freebsd-src/sys/sys/devmap.h

## Purpose
Declares kernel static device mapping support for early boot MMU setup on platforms with `__HAVE_STATIC_DEVMAP`.

## Main Elements
- `struct devmap_entry` maps virtual address, physical address, and region size.
- APIs query last mapped KVA, add auto-allocated entries, register a platform table, bootstrap mappings, and print mappings.

## Dependencies And Integration
Kernel-only; used by MD early boot code and platform memory map setup.

## Risk Notes
Static mappings are established very early. Wrong address/size values can corrupt kernel virtual address layout or overlap other early mappings.

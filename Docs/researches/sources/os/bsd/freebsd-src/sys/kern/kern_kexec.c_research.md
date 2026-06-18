# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_kexec.c

## Purpose
Implements kernel-side staging for `kexec_load(2)`: loads a replacement kernel image into memory and arranges for reboot to jump directly to it instead of firmware reboot.

## Main Elements
- Global staging state includes `staged_image`, mapped staging address, staging VM object, shutdown eventhandler tag, and a mutex.
- `kexec_reboot()` runs during final shutdown when `RB_KEXEC` is set, stops secondary CPUs, disables interrupts, marks the scheduler stopped, and calls machine-dependent `kexec_reboot_md()`.
- `seg_cmp()` sorts segments by destination memory address.
- `segment_fits()` validates that each destination segment lies entirely within a single physical memory segment.
- `pa_for_pindex()` maps staged object page indices back to target physical addresses for page placement.
- `kern_kexec_load()` serializes loads, copies and sorts user segment descriptors, validates segment counts/sizes/ranges, creates a physical VM object, wires pages, swaps object pages so pages already located at target physical addresses are placed at matching indices, maps the object, copies user segment data, zero-fills BSS/MD pages, flushes cache, calls machine-dependent load preparation, and atomically replaces the staged image.
- Passing `nseg == 0` unloads any existing staged image and deregisters the shutdown handler.
- `sys_kexec_load()` enforces securelevel and `PRIV_REBOOT` before delegating.

## Dependencies And Integration
Uses VM physical segment metadata, VM objects/pages/radix, kernel map, pmap/cache operations, shutdown eventhandlers, SMP CPU stop, interrupt disable, reboot flags, and machine-dependent `machine/kexec.h` hooks.

## Risk Notes
This path is inherently risky: it stages physical memory that will be copied during reboot. Validation prevents segments from crossing physical memory regions and avoids target corruption by careful page sorting. Cleanup error paths must match mappings and object sizes precisely; this file contains an error cleanup expression using `kexec_obj->size` while cleaning `new_segments`, which is worth auditing if this code is exercised before any previous image exists.

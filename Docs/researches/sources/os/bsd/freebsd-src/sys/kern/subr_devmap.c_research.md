# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_devmap.c

## Purpose
Provides machine-independent helpers for statically and dynamically mapping device physical memory into kernel virtual address space.

## Key Elements
- Static devmap support under `__HAVE_STATIC_DEVMAP`.
- Static table registration: `devmap_register_table()`.
- Bootstrap mapping: `devmap_bootstrap()`.
- AKVA dynamic static-entry builder: `devmap_add_entry()`.
- Lookup helpers: `devmap_ptov()` and `devmap_vtop()`.
- Public mapping APIs: `pmap_mapdev()`, `pmap_mapdev_attr()`, `pmap_unmapdev()`.
- DDB command: `show devmap` when static devmap and DDB are enabled.

## Behavior
Static mappings are registered before bootstrap and installed with `pmap_preboot_map_attr()` as device memory. `devmap_lastaddr()` reports the lowest KVA consumed by static device mappings.

`pmap_mapdev_attr()` first reuses a static device mapping when possible. Otherwise it rounds the physical range to pages, allocates KVA, and enters mappings with `pmap_kenter()`. Some platforms use special early-boot allocation from the top of KVA, and aarch64 prefers aligned KVA for large mappings. `pmap_unmapdev()` skips static mappings, otherwise removes the device mapping and frees the KVA.

## Research Notes
The file distinguishes firmware/platform-provided static mappings from ad hoc KVA mappings. Static entries are always device-memory mappings; callers asking for a non-device memory attribute cannot use the static table.

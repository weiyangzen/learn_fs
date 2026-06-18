# File Research: sources/os/linux/linux-stable/fs/pstore/ram_internal.h

## Summary
Internal header for ramoops persistent RAM zones.

## Main Responsibilities
- Define PRZ flags for no-lock writes and single-boot old-data zapping.
- Define `struct persistent_ram_zone`, including physical mapping, buffer metadata, ECC state, and old-log storage.
- Declare persistent RAM allocation, free, write, zap, old-log, and ECC reporting helpers.

## Key Interfaces
- `persistent_ram_new()`
- `persistent_ram_free()`
- `persistent_ram_zap()`
- `persistent_ram_write()`
- `persistent_ram_write_user()`
- `persistent_ram_save_old()`
- `persistent_ram_old_size()`
- `persistent_ram_old()`
- `persistent_ram_free_old()`
- `persistent_ram_ecc_string()`

## Cross-File Interactions
Included by `ram.c` and `ram_core.c`; it is the private contract between the ramoops backend and its persistent RAM implementation.

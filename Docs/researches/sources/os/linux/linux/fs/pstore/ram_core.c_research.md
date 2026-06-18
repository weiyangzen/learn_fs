# File Research: sources/os/linux/linux/fs/pstore/ram_core.c

## Role

Implements persistent RAM zone mechanics for ramoops: circular buffer headers, writes, user writes, old-log preservation, memory mapping, and optional Reed-Solomon ECC.

## Persistent Buffer Format

- `struct persistent_ram_buffer` contains:
  - signature;
  - atomic `start`;
  - atomic `size`;
  - flexible data array.
- `PERSISTENT_RAM_SIG` is XORed with a caller-provided signature to identify valid data.

## Circular Buffer Logic

- `buffer_start_add()` advances the circular start pointer with optional locking.
- `buffer_size_add()` grows valid size up to zone capacity.
- `persistent_ram_write()` and `persistent_ram_write_user()` keep only the newest bytes when input exceeds capacity, handle wraparound, update data/header ECC, and return original count on success.
- `persistent_ram_save_old()` copies existing persistent data into a linear `old_log` buffer, applying ECC correction first.
- `persistent_ram_zap()` resets start and size and refreshes header ECC.

## ECC

- Optional ECC uses Reed-Solomon over data blocks plus a separate header parity area.
- `persistent_ram_init_ecc()` carves parity bytes from the end of the zone, initializes `rs_decoder`, allocates parity workspace, and checks/corrects the header.
- `persistent_ram_ecc_old()` checks old data blocks and records corrected byte / bad block counts.
- `persistent_ram_ecc_string()` formats ECC status text for pstore records.

## Memory Mapping

- `persistent_ram_buffer_map()` chooses `vmap()` for valid RAM PFNs and `ioremap()`/`ioremap_wc()` for I/O memory.
- `persistent_ram_vmap()` handles page-granular mappings and preserves byte offsets.
- `persistent_ram_iomap()` requests the memory region before mapping.
- `persistent_ram_free()` unmaps, releases regions, frees RS state, ECC workspace, old logs, labels, and zone objects.

## Research Notes

This file is the durability primitive for ramoops. It validates existing signatures on boot, copies old data before optional zapping, and keeps ECC metadata inside the same reserved region.

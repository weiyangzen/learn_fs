# File Research: sources/os/linux/linux-stable/fs/pstore/ram_core.c

## Summary
Implements persistent RAM zones used by ramoops. It maps physical memory, maintains a circular buffer header, preserves old logs across boot, writes kernel/user data, and optionally protects data with Reed-Solomon ECC.

## Main Responsibilities
- Define `struct persistent_ram_buffer` header with signature, start, size, and data area.
- Map persistent memory using `vmap()` for valid PFNs or `ioremap()`/`ioremap_wc()` for I/O memory.
- Maintain circular write position and valid byte count.
- Copy old persistent data into kernel memory during initialization.
- Write kernel buffers and userspace buffers into circular persistent RAM.
- Encode/decode ECC for data blocks and buffer header.
- Free mappings, ECC state, old logs, labels, and zone structures.

## Key Interfaces
- `persistent_ram_new()` creates and initializes a PRZ.
- `persistent_ram_free()` releases it.
- `persistent_ram_write()` and `persistent_ram_write_user()` append data.
- `persistent_ram_save_old()`, `persistent_ram_old()`, `persistent_ram_old_size()`, and `persistent_ram_free_old()` manage recovered logs.
- `persistent_ram_zap()` clears the live buffer.
- `persistent_ram_ecc_string()` reports ECC correction state.

## Important Behavior
The ring buffer keeps `start` as the oldest valid byte and `size` as valid data length. Writes larger than the zone keep only the tail. Writes may split at the end of the buffer and wrap to offset zero.

ECC space is carved out of the data buffer after mapping. The code reserves parity bytes for each block plus header parity, reduces `buffer_size` accordingly, validates the stored header with ECC, and updates affected parity blocks after writes.

During post-init, a valid signature with sane start/size causes old data to be copied out in logical order. Invalid signatures, invalid counters, or `PRZ_FLAG_ZAP_OLD` cause the live buffer to be reset.

## State and Synchronization
Each PRZ has a raw spinlock unless `PRZ_FLAG_NO_LOCK` is set. The no-lock mode is intended for cases such as per-CPU ftrace where independent writers avoid sharing a zone.

## Cross-File Interactions
`ram.c` uses these APIs for all ramoops storage. `ram_internal.h` exposes the PRZ structure and helper declarations.

## Risks
Persistent memory mapping must match platform memory attributes. ECC sizing can invalidate a zone if parity overhead consumes the buffer. No-lock zones require external design guarantees to avoid concurrent corruption.

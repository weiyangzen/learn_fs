# File Research: sources/teaching/minix/minix/drivers/storage/mmc/mmchost_dummy.c

## Purpose

Implements an in-memory dummy MMC host for testing the generic MMC block layer without real hardware.

## Main Entry Points

- `host_initialize_host_structure_dummy()`: fills the host callback table and initializes slot/card state.
- `dummy_card_initialize()`: sets block size/count, data-transfer state, and full-disk geometry.
- `dummy_host_read()` / `dummy_host_write()`: memcpy data between the caller buffer and the allocated in-memory backing store.
- `dummy_card_release()`: decrements open count and marks the card uninitialized.
- `dummy_host_set_instance()`: accepts only instance 0.

## Control Flow And State

A global `dummy_data` buffer is allocated lazily to `DUMMY_BLOCK_SIZE * DUMMY_SIZE_IN_BLOCKS`. The dummy card exposes one whole-disk partition covering the full buffer. Read and write callbacks use block number and count to compute byte offsets.

## Dependencies

Depends on `mmchost.h`, `sdmmcreg.h`, MINIX logging, and libc allocation/memory routines.

## Risks

No bounds checking exists in dummy read/write callbacks. If the generic block layer passes an out-of-range block, the dummy host will memcpy outside the backing buffer. `init_dummy_sdcard()` allocates backing memory, but `dummy_card_initialize()` does not call it; initialization currently happens during host structure setup.

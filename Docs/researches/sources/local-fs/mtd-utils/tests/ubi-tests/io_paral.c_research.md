# File Research: sources/local-fs/mtd-utils/tests/ubi-tests/io_paral.c

## Role
Parallel UBI volume I/O stress test.

## Main Behavior
- Creates `THREADS_NUM + 1` volumes, with the last static and unchanged to keep wear-leveling pressure.
- Initializes each volume with a full-volume randomized update.
- Starts half the threads doing direct LEB unmap/write/read verification.
- Starts the other half doing randomized volume updates and occasional remove/recreate cycles.
- Cleans up all created volumes and buffers.

## Interfaces And Dependencies
- Uses pthreads, `ubi_mkvol`, `ubi_rmvol`, `ubi_update_start`, `ubi_set_property`, `ubi_leb_unmap`.
- Uses `pread`/`pwrite` for direct eraseblock-size I/O.
- Relies on `initial_check`, `seed_random_generator`, and error helpers.

## Notes
- Uses global `rand()` from multiple threads without synchronization, so randomness is intentionally coarse rather than deterministic per thread.
- Thread functions return `NULL` on failure; `main()` does not collect per-thread success state, so some failures only appear in logs.

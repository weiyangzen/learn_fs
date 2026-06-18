# sources/test-tools/fio/diskutil.c

Purpose: Tracks Linux block device utilization for fio jobs by mapping files to sysfs block devices and periodically accumulating `/sys/block/.../stat` counters.

Important APIs/functions: Public functions are `setup_disk_util()`, `init_disk_util()`, `update_io_ticks()`, and `disk_util_prune_entries()`. Internal helpers locate devices (`get_device_numbers()`, `find_block_dir()`, `read_block_dev_entry()`), add devices and slaves (`disk_util_add()`, `find_add_disk_slaves()`), read stats (`get_io_ticks()`), handle 32-bit stat wrap (`safe_32bit_diff()`), and update accumulated counters (`update_io_tick_disk()`).

Control flow: `setup_disk_util()` creates a global semaphore. `init_disk_util()` skips diskless/nodiskutil jobs, then maps each file to a `disk_util`. Mapping stats the file or parent directory, finds a matching sysfs block directory, normalizes partitions to parent queues, creates a `disk_util`, snapshots initial stats, adds it to global `disk_list`, and recursively adds slave devices. The helper thread calls `update_io_ticks()`, which locks the list, skips work during shutdown, reads each active device's stat file, accumulates deltas, and updates elapsed msec. Prune removes all entries and semaphore state.

State/persistence: Maintains global `disk_list`, a global semaphore, and a last major/minor lookup cache. Each `disk_util` stores sysfs paths, last and accumulated stats, slave links, a per-device lock, timestamps, and user count.

Dependencies/integration: Linux-specific sysfs, fio semaphores, helper thread shutdown, fio file/job iteration, smalloc/sfree, debug logging, and optional Valgrind DRD annotations.

Risks: Extensive path manipulation uses fixed buffers and some `sprintf` calls. Sysfs layout assumptions may fail for unusual devices. Slave discovery increments users and attaches slave list entries; lifetime/refcount correctness is sensitive. `disk_util_mod()` takes an int delta but applies it to unsigned users, so unmatched decrements can underflow.

Test signals: Tests should cover regular files, block devices, missing files, partitions, device-mapper/slave devices, helper shutdown, 32-bit counter wrap, and disabled diskutil engines.

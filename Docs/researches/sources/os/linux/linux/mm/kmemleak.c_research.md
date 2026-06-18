# File Research: sources/os/linux/linux/mm/kmemleak.c

## Role

Implements the Linux kernel memory leak detector. `kmemleak` tracks allocations reported by kernel allocators, stores per-allocation metadata in rbtrees and lists, periodically scans kernel memory for pointer references, and reports allocated objects that appear unreachable through `/sys/kernel/debug/kmemleak`.

## Core Model

- `struct kmemleak_object` is the metadata record for each tracked allocation. It stores allocation address, size, flags, minimum reference count, current reference count, checksum, stack-depot allocation trace, optional scan subareas, creation time, pid, and comm.
- Tracked objects live in `object_list` and in one of three rbtrees:
  - `object_tree_root` for normal virtual addresses.
  - `object_phys_tree_root` for physical-address tracked objects.
  - `object_percpu_tree_root` for percpu allocations.
- Object colors are encoded through `count` and `min_count`:
  - white: not enough references, leak candidate.
  - gray: referenced or explicitly marked false positive.
  - black: ignored and not scanned.
- Object deletion uses `use_count` plus RCU freeing so scans and debugfs iteration can safely traverse metadata while frees occur.

## Locking and Lifetime

- `kmemleak_lock` protects `object_list`, deletion state, and all object rbtrees.
- Each object has `object->lock` protecting mutable metadata and preventing the underlying allocation from being freed while scanned.
- `scan_mutex` serializes memory scans, debugfs control operations, scan-thread state, and gray-list use.
- Required nesting is documented as `scan_mutex -> object->lock -> kmemleak_lock -> other_object->lock`.
- `DELSTATE_NO_DELETE` lets long RCU traversals temporarily reschedule without losing a current object from `object_list`.

## Allocation Tracking

- Public callbacks include:
  - `kmemleak_alloc()`, `kmemleak_free()`, `kmemleak_free_part()`.
  - `kmemleak_alloc_percpu()`, `kmemleak_free_percpu()`.
  - `kmemleak_vmalloc()`.
  - `kmemleak_alloc_phys()`, `kmemleak_free_part_phys()`.
- `__alloc_object()` allocates metadata from a slab cache when available, otherwise from the static emergency pool.
- `__link_object()` inserts metadata into the right rbtree and global list, updates address bounds used to reject impossible pointer values quickly, and rejects overlapping tracked ranges.
- Partial frees split an existing tracked object into left and right remainder objects around the freed range.
- Allocation traces are captured through stack depot after `object_cache` exists.

## Annotation API

- `kmemleak_not_leak()` paints an object gray so it remains scanned but is not reported.
- `kmemleak_ignore()` and `kmemleak_ignore_percpu()` paint objects black so they are not scanned or reported.
- `kmemleak_transient_leak()` resets an object checksum to delay reporting until a later scan.
- `kmemleak_scan_area()` limits scanning to selected subranges inside an object, falling back to full scan if scan-area metadata cannot be allocated.
- `kmemleak_no_scan()` marks an object as not containing references while still allowing references to the object to be found.
- `kmemleak_update_trace()` replaces an object allocation stack trace when the original allocation site is not useful.
- `kmemleak_vmalloc()` handles the `vm_struct` reference by requiring `min_count = 2` and forwarding surplus references via `excess_ref`.

## Scan Algorithm

`kmemleak_scan()` performs a mark-and-sweep style pass:

1. Set `jiffies_last_scan`.
2. Iterate all objects, reset `count` to white, preserve already-gray roots, and blacken physical objects outside lowmem.
3. Scan percpu sections on SMP systems.
4. Scan in-use `struct page` objects for each populated zone under memory-hotplug protection.
5. Optionally scan every task stack.
6. Drain `gray_list`, scanning each referenced object and discovering further references.
7. For still-white objects, compute CRC checksums and temporarily gray recently modified candidates to avoid reporting unstable objects.
8. Drain the gray list again.
9. Report old, still-white, allocated objects as suspected leaks.

Pointers are read word-aligned from scanned memory. Each candidate is KASAN-tag-reset, checked against known address bounds, looked up by alias in the normal and percpu rbtrees, and then used to increment the target object's reference count. Self-references and simple circular `excess_ref` cases are ignored.

## Scanning Details

- Large blocks are scanned in `MAX_SCAN_SIZE` chunks to reduce scheduling latency.
- KASAN and KCSAN are disabled around direct memory reads and checksum generation.
- Per-cpu objects are scanned on every possible CPU.
- Physical objects are scanned through `__va()` only when considered valid lowmem.
- Objects with scan areas scan only those areas unless `OBJECT_FULL_SCAN` is set.
- Checksums use `crc32()` over object contents, with percpu checksums XORed across CPUs.

## Reporting and Debugfs

- `print_unreferenced()` emits address, type, size, task info, a short hex dump, checksum, and allocation backtrace.
- Hex dumps are capped to two rows to avoid seq-file/log spam.
- `kmemleak_seq_*` implements debugfs iteration over reported unreferenced objects.
- `/sys/kernel/debug/kmemleak` write commands support:
  - `off`
  - `stack=on` / `stack=off`
  - `scan=on` / `scan=off`
  - `scan=<seconds>`
  - `scan`
  - `clear`
  - `dump=<address>`
- `clear` either marks currently reported leaks gray or, after disable, frees internal metadata.

## Initialization and Shutdown

- `kmemleak_boot_config()` handles `kmemleak=off` and `kmemleak=on`.
- `kmemleak_init()` initializes timing, metadata caches, and root scan objects for `.data`, `.bss`, and possibly `.data..ro_after_init`.
- `kmemleak_late_init()` creates the debugfs file, starts automatic scanning when configured, and reports remaining emergency-pool capacity.
- `kmemleak_disable()` irreversibly stops allocation/free tracing and schedules cleanup when late init has run.
- Cleanup stops the scan thread, disables free tracing, and frees metadata if no leaks were preserved for later debugfs inspection.

## Dependencies

Uses allocator hooks, debugfs, seq_file, kthreads, rbtrees, stack depot, RCU, memblock, memory-hotplug zone iteration, KASAN/KFENCE/KCSAN integration, percpu APIs, CRC32, and kernel task-stack helpers.

## Research Notes

This file is the full implementation of kmemleak’s runtime: metadata management, leak detection, reporting, debugfs control, and lifecycle. Correctness depends heavily on the documented lock ordering, RCU object lifetime, pointer alias handling, and conservative scan roots. False positives are reduced through minimum age, object annotations, checksums for recently modified objects, task-stack scanning, and explicit gray/black controls.

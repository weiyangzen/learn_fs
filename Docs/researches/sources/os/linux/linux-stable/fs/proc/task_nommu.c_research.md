# File Research: sources/os/linux/linux-stable/fs/proc/task_nommu.c

Implements NOMMU process memory accounting and `/proc/<pid>/maps`.

Key points:
- `task_mem()` estimates process memory using VMA, region, mm, fs, files, sighand, and task object sizes; separates shared vs non-shared memory.
- `task_vsize()` sums VMA ranges.
- `task_statm()` estimates resident/statm values from kernel object sizes and regions.
- `nommu_vma_show()` formats per-process maps lines with permissions, offsets, dev/inode, file path, and `[stack]`.
- Seq iteration pins task and mm, takes `mmap_read_lock_killable()`, and iterates VMAs.
- Exposes only `proc_pid_maps_operations`; smaps/pagemap features are MMU-specific.

Dependencies/contracts:
- NOMMU replacement for selected APIs declared in `internal.h`.
- Uses `proc_mem_open()` for ptrace-gated mm access.

# File Research: sources/os/linux/linux/fs/proc/task_nommu.c

## Scope

This file implements NOMMU per-task memory reporting: task memory summaries, virtual size/statm approximations, and `/proc/<pid>/maps`.

## Public And Internal APIs Covered

- Task memory helpers: `task_mem()`, `task_vsize()`, `task_statm()`.
- Maps operations: `proc_pid_maps_operations`.

## Control Flow And Behavior

- `task_mem()` iterates VMAs under `mmap_read_lock`, accounts VMA objects, backing regions, mm, fs, files, sighand, and task object sizes into private vs shared byte totals based on reference counts and shared mapping flags.
- `task_vsize()` sums VMA ranges under `mmap_read_lock`.
- `task_statm()` estimates total resident size from mm/VMA/region object sizes plus text/data page counts.
- `nommu_vma_show()` prints maps-compatible VMA ranges with permissions, offset, device/inode, path, or `[stack]`.
- The maps seq iterator pins the task and mm, takes `mmap_read_lock_killable()`, initializes a VMA iterator from the last address, and returns VMAs until exhausted.
- `maps_open()` stores the proc inode and obtains an mm through `proc_mem_open()`. Release drops the mm reference.

## Dependencies

- Depends on NOMMU `vm_region`, VMA iteration, `kobjsize()`, process file/fs/sighand reference counters, ptrace-gated `proc_mem_open()`, and seq_file.

## Risks And Invariants

- NOMMU memory accounting is approximate and includes kernel object allocation sizes in addition to mapped region spans.
- Shared/private accounting is based on object reference counts and NOMMU shared mapping flags, not hardware page-table mappings.
- The maps reader must hold task and mm references while iterating.

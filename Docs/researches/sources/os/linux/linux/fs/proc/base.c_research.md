# File Research: sources/os/linux/linux/fs/proc/base.c

## Purpose
Central implementation of per-process and per-thread procfs directories. It defines dynamic `/proc/<pid>` and `/proc/<pid>/task/<tid>` entry tables, lookup/readdir behavior, permissions, inode ownership, symlinks, high-sensitivity files such as `mem` and `map_files`, process control knobs, namespace mapping files, and task dcache invalidation.

## Main Responsibilities
- Defines `struct pid_entry` and macros for PID directory entries.
- Implements `/proc/<pid>/cmdline`, `environ`, `auxv`, `mem`, `cwd`, `root`, `exe`, `wchan`, `stack`, `limits`, `sched`, `oom_*`, `comm`, `timerslack_ns`, and many config-gated entries.
- Enforces hidepid, ptrace, capability, LSM, and same-thread-group permission rules.
- Creates proc inodes tied to task/pid lifetime and updates ownership based on dumpability and credentials.
- Provides dynamic lookup and readdir for PID directories, TID directories, `/task`, `/fd`, `/fdinfo`, `/map_files`, `/attr`, and related subdirectories.
- Exposes user namespace id maps and `setgroups` files.
- Flushes proc dentries for exiting pids.

## Key Interfaces
- Entry helpers: `proc_pid_make_inode()`, `proc_pid_make_base_inode()`, `proc_fill_cache()`.
- Permission/lifetime: `proc_pid_permission()`, `pid_getattr()`, `pid_update_inode()`, `pid_delete_dentry()`, `proc_flush_pid()`.
- Root PID operations: `proc_pid_lookup()`, `proc_pid_readdir()`.
- Task operations: `proc_task_lookup()`, `proc_task_readdir()`, `proc_task_getattr()`.
- Memory access: `proc_mem_open()`, `mem_read()`, `mem_write()`, `mem_lseek()`.
- Link helpers: `proc_pid_link_inode_operations`, `proc_pid_readlink()`, `proc_pid_get_link()`.
- Initialization helper: `set_proc_pid_nlink()`.

## Control Flow and Data Handling
PID directory lookup parses numeric names, finds tasks in the proc superblock’s PID namespace, applies hidepid policy, and instantiates a task-backed directory inode. Readdir emits `self`, `thread-self`, then iterates TGIDs with `find_ge_pid()` while skipping hidden tasks.

PID/TID subentry lookup scans static `pid_entry` arrays and instantiates entries with the right file/inode operations. Directory iteration uses `proc_fill_cache()` to keep dcache inode numbers consistent with stat output.

`/proc/<pid>/mem` opens by acquiring an mm through ptrace-aware `mm_access()`, stores a stable mm reference in `file->private_data`, and reads/writes remote memory page by page via `access_remote_vm()`. The `proc_mem.force_override` early parameter controls when `FOLL_FORCE` is used.

`map_files` parses VMA address ranges from dentry names, verifies exact VMAs under `mmap_lock`, lists file-backed VMAs in two passes, and restricts symlink following to checkpoint/restore capable callers.

## Dependencies and Integration
Integrates with procfs root/inode internals, pid namespaces, user namespaces, ptrace, LSM hooks, cgroups, cpuset, memory management, VMA iteration, scheduler, audit, OOM, file descriptors, mount namespace files, proc page-monitor files, timers, KSM, livepatch, seccomp, networking, and architecture hooks.

## Concurrency and Lifetime Notes
Task references are acquired with `get_proc_task()`, `get_pid_task()`, or RCU lookups. Sensitive task state is protected by task locks, `exec_update_lock`, signal locks, mmap locks, inode locks, and namespace/capability checks. Proc directory inodes are linked into pid inode lists so `proc_flush_pid()` can invalidate dentries on exit.

## Risks and Review Hotspots
- `/proc/<pid>/mem`, `map_files`, symlink resolution, and stack/wchan output are security-critical.
- hidepid and ptrace checks must stay consistent across lookup, getattr, readdir, and open/read paths.
- PID/TID readdir uses position cookies and cached TID fallback; seek/short-read behavior is ABI-sensitive.
- `pid_entry` tables define proc ABI surface; adding entries affects permissions, nlink counts, and userspace.
- Inode ownership depends on dumpability and credentials and can change at runtime.

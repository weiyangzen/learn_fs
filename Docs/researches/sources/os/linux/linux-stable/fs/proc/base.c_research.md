# File Research: sources/os/linux/linux-stable/fs/proc/base.c

## Purpose

Implements the per-process and per-thread procfs hierarchy: `/proc/<pid>`, `/proc/<pid>/task/<tid>`, task symlinks, memory-related files, credentials/security attributes, scheduler/OOM controls, namespace/id maps, and directory lookup/readdir behavior.

## Main Responsibilities

- Defines per-entry descriptors:
  - `struct pid_entry` and macros `DIR`, `LNK`, `REG`, `ONE`, `ATTR`.
  - Static entry tables `tgid_base_stuff[]` and `tid_base_stuff[]`.
- Implements cmdline reading:
  - `get_mm_cmdline()` reads argv memory, including special `setproctitle()` handling.
  - `proc_pid_cmdline_read()` exposes `/proc/<pid>/cmdline`.
- Implements debugging/introspection files:
  - `proc_pid_wchan()` under `CONFIG_KALLSYMS`.
  - `proc_pid_stack()` under `CONFIG_STACKTRACE`, restricted to `CAP_SYS_ADMIN`.
  - `proc_pid_schedstat()` under `CONFIG_SCHED_INFO`.
  - `proc_pid_syscall()` under `CONFIG_HAVE_ARCH_TRACEHOOK`.
  - `proc_pid_personality()`, livepatch patch state, KSM stats, stack depth metrics.
- Implements `/proc/<pid>/mem`, `environ`, and `auxv`:
  - `proc_mem_open()` uses `mm_access()` and pins `mm_struct` lifetime.
  - `mem_rw()` performs remote memory access page by page.
  - `proc_mem.force_override=` early parameter controls `FOLL_FORCE` behavior.
  - `environ_read()` reads environment memory.
  - `auxv_read()` reads saved auxiliary vector.
- Implements OOM knobs:
  - `proc_oom_score()`, `oom_adj_read/write()`, and `oom_score_adj_read/write()`.
  - `__set_oom_adj()` enforces privilege rules and propagates score changes to processes sharing an mm when appropriate.
- Implements audit/fault/scheduler/time controls:
  - `loginuid` and `sessionid` under `CONFIG_AUDIT`.
  - Fault injection knobs under `CONFIG_FAULT_INJECTION`.
  - `sched`, `autogroup`, and `timens_offsets`.
  - `comm` read/write with same-thread-group restriction for renaming.
- Implements symlink behavior:
  - `proc_cwd_link()`, `proc_root_link()`, `proc_exe_link()`.
  - `proc_pid_get_link()` and `proc_pid_readlink()` check fd-style access permissions before resolving paths.
- Builds proc inodes and dentries:
  - `task_dump_owner()` computes ownership based on dumpability, credentials, user namespace, and kernel-thread state.
  - `proc_pid_make_inode()` and `proc_pid_make_base_inode()` allocate proc inodes and attach pid references.
  - `pid_revalidate()` updates dynamic ownership on lookup revalidation.
  - `pid_delete_dentry()` drops dead task dentries.
  - `proc_fill_cache()` instantiates dentries during readdir to keep readdir inode numbers consistent with stat.
- Implements `/proc/<pid>/map_files`:
  - Parses VMA address names with `dname_to_vma_addr()`.
  - Validates exact VMAs in `map_files_d_revalidate()`.
  - Resolves mapped file paths with `map_files_get_link()`.
  - Restricts symlink following to checkpoint/restore capable users.
  - Uses two-pass readdir to avoid holding `mmap_lock` during dentry instantiation.
- Implements POSIX timers and timerslack:
  - `/proc/<pid>/timers` under checkpoint/restore and POSIX timers.
  - `timerslack_ns` read/write with `CAP_SYS_NICE` and scheduler LSM checks for other tasks.
- Implements LSM attributes under `/proc/<pid>/attr`:
  - Reads/writes through `security_getprocattr()` and `security_setprocattr()`.
  - Writes are restricted to the current task and opener mm, and protected by `cred_guard_mutex`.
  - Optional Smack/AppArmor subdirectories are generated with macro helpers.
- Implements coredump filter, IO accounting, and user namespace maps:
  - `coredump_filter` under `CONFIG_ELF_CORE`.
  - `io` under `CONFIG_TASK_IO_ACCOUNTING`, gated by ptrace checks.
  - `uid_map`, `gid_map`, `projid_map`, `setgroups` under `CONFIG_USER_NS`.
- Implements directory lookup and iteration:
  - `proc_pid_lookup()` looks up numeric `/proc/<pid>` entries.
  - `proc_pid_readdir()` emits `self`, `thread-self`, and visible tgids.
  - `proc_task_lookup()` and `proc_task_readdir()` handle `/proc/<pid>/task/<tid>`.
  - `proc_dir_llseek()` preserves a cached tid cookie across partial readdir.

## Permission Model

- The file’s header warns that proc permission checks must happen at operation time, because task state changes dynamically.
- `hidepid` policy is centralized in `has_pid_permissions()` and `proc_pid_permission()`.
- Many sensitive reads use `ptrace_may_access()` with `PTRACE_MODE_READ_FSCREDS` or attach modes.
- `map_files` symlink following is additionally restricted to checkpoint/restore capability.
- `/proc/<pid>/task/<tid>/comm` has special same-thread-group permissions for pthread naming compatibility.
- Write operations for OOM, loginuid, fault injection, scheduler, time namespace, and LSM attrs include targeted capability or ownership checks.

## Lifetime and Concurrency Notes

- Task references are acquired through `get_proc_task()`, `get_pid_task()`, or pid namespace lookup, and released promptly.
- `mm_struct` lifetime is pinned with `mmgrab()` for `/mem`-style open files but memory itself is not pinned.
- Signal data uses `lock_task_sighand()` or `exec_update_lock` depending on operation.
- `/map_files` uses `mmap_read_lock_killable()` and releases it before `proc_fill_cache()`.
- Base directory inodes are linked into `pid->inodes` so `proc_flush_pid()` can invalidate dentries on task exit.

## Entry Tables

- `tgid_base_stuff[]` defines process-level entries including `task`, `fd`, `map_files`, `fdinfo`, `ns`, `net`, `environ`, `auxv`, `status`, `limits`, `sched`, `cmdline`, `stat`, `maps`, `mem`, symlinks, mounts, page monitor files, attrs, OOM knobs, namespace maps, timers, KSM and optional debug files.
- `tid_base_stuff[]` defines analogous thread-level entries, with differences such as `children` under `CONFIG_PROC_CHILDREN` and special `comm` inode operations.

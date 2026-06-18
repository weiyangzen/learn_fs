# File Research: sources/os/linux/linux/fs/coredump.c

## Purpose
Implements Linux VFS coredump orchestration: core pattern expansion, file/pipe/socket targets, process-thread coordination, dump writing helpers, sysctls, and VMA dump selection/snapshotting.

## Main Elements
- Core target model: `struct core_name` tracks generated target name, type (`file`, `pipe`, `socket`, socket request), wait/dump mask, pipe-limit state, and whether a dump was produced.
- Pattern expansion: `coredump_parse()` processes `core_pattern`, handles `%` specifiers for pids/uids/gids/signal/time/hostname/executable/core limit/cpu/pidfd, splits pipe argv, and validates socket paths.
- Thread-group coordination: `zap_process()`, `zap_threads()`, `coredump_wait()`, and `coredump_finish()` stop sibling threads, wait for them to quiesce, and release them after dumping.
- Pipe helper support: `umh_coredump_setup()` installs pipe stdin and optional pidfd fd 3; `coredump_pipe()` enforces recursion and `core_pipe_limit`, spawns the helper, and captures its write pipe.
- Socket support: under `CONFIG_UNIX`, `coredump_sock_connect()`, request/ack helpers, `coredump_sock_request()`, and `coredump_socket()` connect to AF_UNIX handlers and negotiate whether kernel/userspace/reject/wait handling is requested.
- File target support: `coredump_file()` opens/unlinks/truncates regular core files, enforces suid-safe absolute path rules, owner/mode preservation, regular-file-only behavior, and minimum coredump size.
- Main flow: `vfs_coredump()` snapshots credentials/dumpability/limits, waits for coredump ownership, then `do_coredump()` selects target, unshares files, writes via `binfmt->core_dump()`, handles socket shutdown/waiting, and cleans up.
- Dump helpers: `dump_emit()`, `dump_skip_to()`, `dump_skip()`, `dump_align()`, and `dump_user_range()` are exported helpers used by binary-format core writers.
- Sysctls: registers `kernel.core_uses_pid`, `core_pattern`, `core_pipe_limit`, `core_file_note_size_limit`, `core_sort_vma`, and readonly `core_modes`.
- VMA policy: `always_dump_vma()`, `vma_dump_size()`, `coredump_next_vma()`, `dump_vma_snapshot()`, and `free_vma_snapshot()` decide which VMAs to dump, optionally sort by size, and hold file references for core metadata.

## Dependencies And Integration
Integrates process signal state, binfmt core dump callbacks, VFS file creation/writes, pipes, usermode helpers, pidfs, AF_UNIX sockets, sysctls, LSM/security audit, namespaces, mm/VMA iteration, and tracepoints.

## Risk Notes
Core dumping sits at process-death time and must avoid deadlocks, recursion, stale pid references, unsafe suid dumps, and partial output confusion. Socket mode adds protocol validation and initial namespace/path restrictions. VMA snapshotting takes the mmap write lock and later probes possible ELF headers outside the lock, so interruption and lifetime handling are key.

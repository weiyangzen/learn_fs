# sources/test-tools/stress-ng/stress-filerace.c

Purpose: implements `filerace`, a multi-process shared-directory stressor that races many file, directory, metadata, allocation, locking, ACL, and lookup operations against a small evolving filename set.

Important APIs/types/functions: `stress_filerace_fops[]` is the central operation table, spanning stat/lseek/sync/read/write/pread/pwrite/fallocate/truncate/time updates/flock/FIBMAP/fadvise/fallocate/open/statx/readlink/openmany/leases/lockf/OFD locks/chdir/mmap/rw hints/ACL/access/name_to_handle/sendfile. `stress_filerace_file()` selects a random operation mix on odd seconds and a uniform operation on even seconds. `stress_filerace_filename()` maps elapsed time to two-digit hex names, slowly widening the collision set. `stress_filerace_child()` performs high-level create, unlink, open, rename, directory, link/symlink, mkdir, mass-open, and getdents actions while keeping up to 128 fds open.

Control flow: `stress_filerace()` records uid/gid and start time, installs SIGIO handling, creates a temp directory, forks `--filerace-procs` children, and runs the same child loop in the parent. Each child repeatedly chooses one of eleven directory/file scenarios, calls lower-level fops on opened fds, occasionally forks again while closing a full fd batch, and parent-side iterations increment bogo operations. Cleanup kills children and removes files/directories left in the temp path.

State and persistence behavior: global uid/gid/t_start guide ownership and filename selection. The stressor creates a temporary directory containing a bounded but constantly changing set of files, directories, and symlinks. It may mutate permissions, ownership, ACLs, extents, file size, locks, and timestamps; cleanup removes residual entries.

Dependencies and integration points: feature coverage depends on Linux fs headers, ACL libraries, sendfile, lock APIs, fallocate flags, statx/name_to_handle, and mmap/msync support. Integrates with stress-ng temp dirs, OOM includes, kill/wait helpers, random helpers, usage reporting, and signal handling. Registered as `CLASS_FILESYSTEM | CLASS_OS`, `VERIFY_NONE`.

Risks: this stressor intentionally creates races and ignores many expected errors, so it is useful for kernel/filesystem robustness rather than deterministic correctness. ACL and ownership operations may fail without privileges or filesystem support. The mmap operation installs temporary SIGBUS/SIGSEGV handlers because concurrent truncation/hole punching can invalidate mappings. One branch checks `if (tmp_fd != 1)` before closing, likely intending `!= -1`, which can leak fd 1 semantics or skip close if fd 1 is returned.

Test signals: run with `--filerace-procs` at 1, default, and 64 on filesystems with and without ACL/fallocate/statx support. Check for lingering temp entries, unexpected signal deaths, fd leaks, and stability under concurrent instances.

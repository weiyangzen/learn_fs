# sources/test-tools/stress-ng/stress-procfs.c research

Purpose: implements the `procfs` stressor, which aggressively traverses `/proc`, opens entries, performs reads, seeks, ioctls, polls, occasional writes, and special-case proc file exercises.

Important APIs, types, and functions: `stress_ctxt_t` carries worker arguments and writeability; `stress_proc_info_t` maps special proc paths to handlers. `stress_proc_self_mem()` validates `/proc/self/mem` against an anonymous mapping. Optional handlers exercise `/proc/mtrr` and `/proc/bus/pci` ioctls. `stress_proc_rw()` is the core per-file exerciser; `stress_proc_dir()` recursively scans directories; `stress_proc_rw_thread()` runs helper threads against the current shared path protected by a shim spinlock.

Control flow: `stress_procfs()` scans `/proc`, initializes a global `proc_path` and spinlock, starts four pthread reader loops, synchronizes, then iterates shuffled `/proc` entries and random process directories. For regular files and symlinks it publishes the path to helper threads and also calls `stress_proc_rw()` directly. Shutdown clears `proc_path`, cancels/join threads, destroys the spinlock, and frees scandir entries.

State and persistence: global `proc_path`, `mixup`, signal set, and spinlock coordinate transient thread activity. No persistent output is produced; all file operations target kernel virtual procfs entries and temporary buffers.

Dependencies and integration: gated by pthread support plus Linux or Cygwin. It uses `scandir`, `open`, `read`, `lseek`, `mmap`, `ioctl`, `poll`/`ppoll`, namespace ioctls, stress-ng filesystem helpers, capabilities, hashing, and randomization. Metadata classifies it as filesystem and OS.

Risks: `/proc` entries can block, disappear, or have side effects, so the code uses nonblocking opens, timeout thresholds, recursion depth limits, and skips char/block/fifo/socket reads. Concurrent access is intentionally racy and may expose kernel bugs; Cygwin and SH4 exclusions document known hazards.

Test signals: skip when `/proc` is unavailable, bogo increments during traversal, special-path exercise coverage, timeout paths, and absence of hangs or leaked helper threads are the main signals.

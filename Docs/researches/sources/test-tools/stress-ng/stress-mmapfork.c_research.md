# sources/test-tools/stress-ng/stress-mmapfork.c

Purpose: implements the `mmapfork` VM/scheduler stressor. It repeatedly forks many short-lived child processes, and each child sizes, maps, advises, touches, and unmaps shared anonymous memory to stress fork-time VM accounting, mmap population, memory advice, and child cleanup.

Important APIs/types/functions: `stress_mmapfork_info` registers options `mmapfork-bytes` and `mmapfork-procs`. `stress_mmapfork()` owns the worker loop, child fan-out, memory sizing via `sysinfo()`, optional `MADV_WIPEONFORK` verification, and SIGSEGV attribution. `stress_segvhandler()` exits with a stage-specific bitmask, `should_terminate()` detects parent death or stop requests, and `notrunc_strlcat()` builds a bounded debug reason string.

Control flow: the parent initializes optional wipe-on-fork test memory, synchronizes, then loops creating up to the configured child count. Each child installs failure/scheduler settings, checks `sysinfo()`, derives its per-child mapping length from free RAM, instances, and process count, then runs `stress_mmap_populate()`, optional `MADV_WILLNEED`, `memset`, optional `MADV_DONTNEED`, and `stress_munmap_force()`. The parent waits for children, kills leftovers on interruption, increments bogo operations, and reports any stage-specific SIGSEGV exits.

State and persistence: persistent state is limited to the optional wipe-on-fork page, child PID array, and static `segv_ret`. No filesystem state is created. Child mappings are anonymous and forcibly unmapped or released at exit.

Dependencies and integration: requires `sysinfo()` support; uses stress-ng process state, synchronization, kill/wait helpers, scheduler application, parent-death alarm, mmap helpers, settings, and memory usage reporting.

Risks and test signals: high process fan-out and memory pressure can trigger fork or mmap resource exhaustion. Correct behavior is child reaping without leaks, optional `MADV_WIPEONFORK` verification, bogo increments, and debug-only SIGSEGV stage counts rather than hard failure for expected pressure paths.

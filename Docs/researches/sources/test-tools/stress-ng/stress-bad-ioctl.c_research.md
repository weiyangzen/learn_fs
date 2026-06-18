<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-bad-ioctl.c -->
# sources/test-tools/stress-ng/stress-bad-ioctl.c

Purpose: `stress-bad-ioctl.c` implements the Linux `bad-ioctl` stressor. It discovers character/block devices under `/dev` and issues malformed read/write ioctl commands and invalid user pointers to exercise driver error paths without requiring device-specific knowledge.

Important APIs/types/functions: Linux, pthreads, and `_IOR` are required. `dev_ioctl_info_t` stores device paths in a binary tree, ignore state, current 16-bit ioctl type/number state, and per-thread exercised flags. `stress_bad_ioctl_dev_dir()` recursively scans `/dev`, skipping dot entries, many numbered sibling devices, and watchdog paths. `stress_bad_ioctl_rw()` maps two pages, unmaps the second to create boundary pointers, opens the selected device, and calls `ioctl()` with `_IOR` and optional `_IOW` commands using end-of-page, NULL, `PROT_NONE`, and read-only pointers. `stress_bad_ioctl_dir()` selects devices and advances ioctl command generation by `inc`, `random`, `random-inc`, or `stride`.

Control flow: the top-level stressor builds the device tree, syncs, then repeatedly forks a child. The child installs a `SIGSEGV` longjmp handler, creates a lock, marks itself OOM-killable, starts up to four pthreads that continuously call `stress_bad_ioctl_rw()`, and also walks the device tree in the controlling thread. The parent waits for the child and restarts while the stressor continues.

State and persistence behavior: persistent state is only the in-memory device tree and per-node command state. Child threads share global `lock` and `dev_ioctl_node`; each node tracks whether all threads have exercised it before advancing the ioctl command. No files are created.

Dependencies and integration points: integrates with stress-ng option parsing, pthread wrappers, lock helpers, try-open timeouts, signal longjmp, mapped guard pages (`args->mapped->page_none/page_ro`), OOM adjustment, and fork retry logic. It is registered as `CLASS_DEV | CLASS_OS | CLASS_PATHOLOGICAL`.

Risks: issuing arbitrary ioctls to real device drivers is inherently high risk; the code avoids watchdogs but still depends on drivers returning errors promptly. A 0.25-second threshold limits slow calls per device but cannot prevent all hangs. The tree scan only includes world/group-readable/writable directories, which reduces coverage on locked-down systems.

Test signals: test with all four `bad-ioctl-method` values, no accessible devices, devices that fail `open`, device calls that trigger `SIGSEGV`, pthread creation failures, and immediate stop. Failures appear as unexpected child exit or `caught an unexpected segmentation fault`.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-bad-ioctl.c -->

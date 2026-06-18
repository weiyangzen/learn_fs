# sources/security-integrity/audit-userspace/auparse/clone-flagtab.h

Purpose: Build-time 64-bit table mapping Linux `clone`/`clone3` flag bits to symbolic names.

Important APIs, types, and functions: Contains `_S(ULL, "CLONE_*")` rows for process/thread namespace and behavior flags, including `CLONE_CLEAR_SIGHAND` and `CLONE_INTO_CGROUP`. `Makefile.am` uses `gen_tables64.c` and `--64bit --i2s-transtab clone_flag` to generate `clone-flagtabs.h`.

Control flow: No runtime flow.

State and persistence: Static source for generated 64-bit translation data.

Dependencies and integration points: Values are tied to `include/uapi/linux/sched.h` and used by auparse interpretation of clone flags.

Risks and edge cases: Clone flag values include high bits, so 64-bit generation is necessary; using 32-bit table machinery would truncate newer flags. Kernel changes require updates.

Test signals: Generated table build and interpretation tests for clone flag bitmasks.

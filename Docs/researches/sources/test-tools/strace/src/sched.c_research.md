# sources/test-tools/strace/src/sched.c

Purpose: decodes scheduler policy, priority, round-robin interval, and `sched_attr` based syscalls.

Important APIs/types/functions: `sprint_policy`, `print_policy`, `print_sched_param`, `do_sched_rr_get_interval`, `print_sched_attr`, and syscall handlers for `sched_getscheduler`, `sched_setscheduler`, `sched_getparam`, `sched_setparam`, `sched_get_priority_min`, `sched_rr_get_interval_time32/time64`, `sched_setattr`, and `sched_getattr`.

Control flow: simple scheduler syscalls print pid and policy/parameter arguments on entry and output parameters on exit. `sched_getscheduler` returns a symbolic aux string for successful return values. `sched_rr_get_interval` shares a helper parameterized by timespec32/timespec64 printers. `print_sched_attr` first reads the user-supplied size, fetches only the available struct version, handles `sched_setattr` keep-policy/keep-params flags, and prints `...` when user/kernel sizes indicate newer fields.

State and persistence behavior: stateless except temporary stack copies. It does not modify tracee memory; it reports kernel-written `attr.size` changes on `sched_setattr` `E2BIG`.

Dependencies and integration points: uses Linux `sched_attr`, xlat tables for policies and flags, pid printers, and time printers. AArch64 has special high-word error formatting for `sched_getattr` size due to a kernel/compiler ABI issue.

Risks: `sched_attr` is versioned and growing; fields must stay aligned with kernel `SCHED_ATTR_SIZE_VER*` constants. `SCHED_FLAG_KEEP_POLICY`/`KEEP_PARAMS` suppress fields in set mode, so tests need both keep and normal paths.

Test signals: cover known/unknown policies, `SCHED_RESET_ON_FORK`, get/set param, time32/time64 RR intervals, `sched_setattr` with size 0, old/new sizes, `E2BIG`, util clamp fields, keep flags, and `sched_getattr` flags.

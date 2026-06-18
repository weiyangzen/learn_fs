# sources/test-tools/stress-ng/core-sched.c

Purpose: centralizes scheduler policy names, option parsing, scheduler application, deadline scheduling support, and sched_ext status reporting.

Important APIs/types/functions: `stress_sched_types` lists available scheduler constants with user names and macro names. `stress_sched_name_get` maps policy to name. `stress_sched_set` validates priority and applies scheduler state. `stress_sched_parse` validates option strings. `stress_sched_settings_apply` reads stored settings for the current process. `stress_sched_ext_ops_get` reads the active sched_ext ops name from sysfs.

Control flow: `stress_sched_set` returns immediately for `UNDEFINED`. FIFO/RR policies validate priority against kernel min/max, defaulting to max under aggressive mode or midpoint otherwise. Deadline scheduling builds `shim_sched_attr`, reads `sched-period`, `sched-runtime`, and `sched-deadline` settings, uses defaults if no deadline is supplied, and calls `shim_sched_setattr`, returning `-E2BIG` specially for attribute-size mismatch. Other policies ignore explicit priorities and call `sched_setscheduler`. Unsupported platforms get a no-op shim implementation. `stress_sched_ext_ops_get` returns "unknown" by default, treats disabled/unreadable sched_ext as nonfatal, and truncates ops names after newline or repeated separators.

State and persistence: no private persistent state beyond constant scheduler table. It mutates kernel scheduling policy for the target PID, which persists until changed or process exit.

Dependencies/integration: uses `core-setting` to retrieve parsed global scheduler options, shim sched_attr syscalls, global `g_opt_flags`, and filesystem helpers for `/sys/kernel/sched_ext`.

Risks: setting real-time/deadline policies can fail due to permissions or resource limits. Deadline default values are embedded here and may not suit all kernels. `SCHED_EXT` is defined as 7 on Linux if absent, which enables parsing even on older headers but does not guarantee runtime support.

Test signals: parse all compiled policy names, apply quiet/nonquiet paths without privileges, mock `shim_sched_setattr` E2BIG, and test sched_ext sysfs disabled/enabled strings.

# sources/test-tools/stress-ng/core-capabilities.h

Purpose: maps Linux capability constants to stress-ng `SHIM_CAP_*` names with root fallback.

Important APIs and control flow: defines `SHIM_CAP_IS_ROOT`, many POSIX/Linux capability aliases, and declares getset/check/drop functions. Missing capability macros map to `SHIM_CAP_IS_ROOT`.

State and persistence: compile-time mapping only.

Dependencies and integration: centralizes privilege checks for stressors requiring raw I/O, network admin, BPF, perf, sys_admin, and related permissions.

Risks and test signals: fallback to root may be coarser than actual platform permission model; new Linux capabilities require updates. Signal is correct compile on older headers and proper stressor skip/permission behavior.

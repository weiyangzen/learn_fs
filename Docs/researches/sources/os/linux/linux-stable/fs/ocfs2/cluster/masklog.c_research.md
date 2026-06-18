# File Research: sources/os/linux/linux-stable/fs/ocfs2/cluster/masklog.c

## Summary
Implements OCFS2/O2CB runtime log-mask control. It maintains global allow/deny masks, prints formatted masked log messages, and exposes per-mask sysfs attributes under the O2CB kset.

## Main Responsibilities
- Store global `mlog_and_bits` and `mlog_not_bits`.
- Convert each mask bit between `allow`, `deny`, and `off`.
- Print enabled messages with task, pid, CPU, function, line, severity, and formatted payload.
- Define sysfs attributes for every supported mask bit.
- Register/unregister the `logmask` kset.

## Key Interfaces
- `__mlog_printk()` is called by the `mlog()` macro after compile/runtime mask checks.
- `mlog_sys_init()` installs the sysfs logmask kset.
- `mlog_sys_shutdown()` unregisters it.

## Important Behavior
`ML_ERROR` maps to `KERN_ERR` with an `ERROR:` prefix, `ML_NOTICE` maps to `KERN_NOTICE`, and other enabled masks use `KERN_INFO`. A message is suppressed if its mask is not allowed or is explicitly denied.

## Risks
The sysfs mask table must stay aligned with mask definitions in `masklog.h`; adding a new bit requires updating both files.

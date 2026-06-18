# File Research: sources/os/linux/linux-stable/fs/ocfs2/cluster/sys.h

## Summary
Declares the O2CB sysfs lifecycle API.

## Main Responsibilities
- Provide include guard for cluster sysfs declarations.
- Declare `o2cb_sys_init()` and `o2cb_sys_shutdown()`.

## Key Interfaces
- Nodemanager module init calls `o2cb_sys_init()`.
- Nodemanager module exit calls `o2cb_sys_shutdown()`.

## Risks
Small lifecycle header; correctness depends on callers preserving init/exit ordering with masklog and configfs.

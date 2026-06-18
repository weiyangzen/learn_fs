# File Research: sources/os/bsd/dragonflybsd/sys/sys/dsched.h

Kernel disk scheduler integration stub/header.

Key responsibilities:
- Defines disk scheduler policy name length.
- Declares hooks for disk create, update, and destroy.
- Provides placeholder no-op macros for future buffer/process/thread enter/exit accounting.

Dependencies:
- Kernel-only; includes queue, bio, biotrack, lock, conf, msgport, sysctl, and disk headers.

Notable risks:
- Most hooks are placeholders, so consumers may assume scheduling/accounting exists when macros currently compile away.
- Disk scheduler lifecycle must track disk create/update/destroy with disk_info changes.

# File Research: sources/virtualization/open-iscsi/usr/fwparam_ibft/fwparam.h

Shared firmware parameter header. It defines `FILENAMESZ` as 1024 and declares sysfs and PPC firmware boot-info/target-list functions.

The API operates on `struct boot_context` and `struct list_head`, allowing `fw_entry.c` to choose PPC or sysfs implementations without knowing their internals.

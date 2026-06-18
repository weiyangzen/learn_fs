# File Research: sources/os/bsd/netbsd-src/sys/sys/selinfo.h

Read completely: 83 lines.

This header defines `struct selinfo`, the kernel state object for processes and knotes waiting for I/O readiness. It stores collision CPU masks, a kqueue list, cluster association, first LWP to notify, selected descriptor info, LWP-list linkage, and reserved fields.

Risks: the structure is embedded in device/socket state and is manipulated by select and kqueue paths. Lifetime must outlast registered waiters and knotes.

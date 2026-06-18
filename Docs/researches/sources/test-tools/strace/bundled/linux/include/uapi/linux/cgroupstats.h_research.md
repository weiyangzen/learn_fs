# sources/test-tools/strace/bundled/linux/include/uapi/linux/cgroupstats.h

Purpose: defines the taskstats-based cgroup statistics ABI. It lets userspace request and receive per-cgroup task state counts via generic netlink/taskstats.

Important APIs/types/functions: `struct cgroupstats` contains five 64-bit counters: sleeping, running, stopped, uninterruptible, and I/O wait. Command IDs start at `__TASKSTATS_CMD_MAX` and include `CGROUPSTATS_CMD_GET`, `CGROUPSTATS_CMD_NEW`, and max macros. Attribute/type enums define `CGROUPSTATS_TYPE_CGROUP_STATS` and `CGROUPSTATS_CMD_ATTR_FD`.

Control flow: no executable control flow exists. The ABI flow implied by the declarations is userspace sending a GET command with a cgroup file descriptor attribute and receiving a stats payload or kernel event.

State and persistence behavior: values are snapshots of live task state derived from `task->state`; there is no persistent storage in the header. Each member is documented as 8-byte aligned for cross-architecture ABI stability.

Dependencies: includes `<linux/types.h>` and `<linux/taskstats.h>`, and it relies on taskstats command numbering to avoid collisions.

Integration points: strace can decode taskstats generic netlink messages, command IDs, attributes, and the returned cgroup stats struct. Kernel integration is through taskstats, not a standalone syscall.

Risks: command numbering depends on `__TASKSTATS_CMD_MAX`, so stale bundled taskstats headers can mislabel messages. Because counters are snapshots, tests must not assume stable values across a running system.

Test signals: decode tests should cover `CGROUPSTATS_CMD_GET` with `CGROUPSTATS_CMD_ATTR_FD`, a response containing `CGROUPSTATS_TYPE_CGROUP_STATS`, and max-value rendering for unknown future attributes.

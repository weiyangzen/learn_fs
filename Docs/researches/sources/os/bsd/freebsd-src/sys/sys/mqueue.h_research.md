# File Research: sources/os/bsd/freebsd-src/sys/sys/mqueue.h

Defines POSIX message queue attribute structure.

Key content:
- `struct mq_attr` includes:
  - `mq_flags`
  - `mq_maxmsg`
  - `mq_msgsize`
  - `mq_curmsgs`
  - four reserved longs, ignored on input and zeroed on output.

Research relevance:
- Minimal user/kernel ABI for POSIX message queues.
- Included in this group as a small IPC header, not directly VFS-specific.

Cautions:
- Only attributes are defined here; queue operations and implementation live elsewhere.
- Reserved fields are part of ABI padding/forward compatibility.

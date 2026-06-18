# File Research: sources/os/bsd/netbsd-src/sys/sys/socketvar.h

Read completely: 611 lines.

This kernel socket-internals header defines socket buffer state, socket objects, state flags, accept filters, socket option transport, core socket/file operations, syscall helpers, and inline readiness/accounting helpers.

`struct sockbuf` stores select state, mbuf owner, back pointer, condition variable, byte/mbuf counters, watermarks, mbuf chain pointers, flags, timeout, and overflow count. `struct socket` stores locking, type/options/state, protocol PCB/switch, accept queues, errors, process group, OOB mark, send/receive buffers, upcall and protocol send/receive hooks, mbuf/uid/credential ownership, and accept-filter state.

APIs cover socket file operations, sockbuf append/drop/flush/reserve/wait, socket init/create/connect/listen/accept/send/receive/shutdown/close, option get/set, sockname/control-message copyout, syscall helper entry points, locking/refcount helpers, and accept-filter management. Inline functions implement `sb_notify`, `sbspace`, `soreadable`, `sowritable`, buffer accounting, wakeups, and socket locking.

Risks: most operations assert the socket lock. Buffer counters are unsigned and overflow-aware in `sbspace`, while manual `sballoc`/`sbfree` updates must track mbuf external storage. Accept queues, abort references, upcalls, and lock pointer replacement make lifetime and locking subtle.

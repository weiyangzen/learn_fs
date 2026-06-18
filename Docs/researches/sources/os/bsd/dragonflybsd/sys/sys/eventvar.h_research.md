# File Research: sources/os/bsd/dragonflybsd/sys/sys/eventvar.h

`eventvar.h` is a kernel-structure header for internal kqueue state and rejects normal userland inclusion. It includes queue, event, thread, and filedesc definitions.

It defines `KQ_NEVENTS`, `KQEXTENT`, `TAILQ_HEAD(kqlist, knote)`, and `struct kqueue`, including pending/all knote lists, pending count, async signal owner, attached `kqinfo`, file descriptor table pointer, state, sleep count, registration thread, and knote hash table.

The state flags are `KQ_ASYNC` and `KQ_REGWAIT`. This header is consumed by kernel kqueue implementation and structures that embed or inspect kqueues.

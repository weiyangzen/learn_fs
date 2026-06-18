# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_jaildesc.c

## Purpose
Implements jail descriptors: passable file descriptors that refer to a jail, support permission-carrying operations, allow kqueue/poll notifications, and optionally own jail lifetime/removal.

## Main Elements
- Defines `jaildesc_ops` as a `DTYPE_JAILDESC` fileops table with invalid read/write/ioctl/truncate and custom poll, kqfilter, stat, close, kinfo, and compare operations.
- `jaildesc_alloc()` creates an unassociated descriptor, checks `PRIV_JAIL_REMOVE` for owning descriptors, allocates a file, sets read/write access based on `PRIV_JAIL_SET`, and initializes locks/knlist state.
- `jaildesc_find()` resolves a descriptor fd, validates type and prison liveness, and optionally returns held prison and descriptor credentials.
- `jaildesc_set_prison()` attaches a descriptor to a locked prison and holds the prison.
- `jaildesc_prison_cleanup()` detaches all descriptors from a prison during jail teardown.
- `jaildesc_knote()` propagates jail lifecycle/child/attach events to descriptor listeners and marks removed descriptors hung up.
- `jaildesc_close()` detaches or removes the referenced prison depending on `JDF_OWNING`, drains selection/kqueue state, destroys locks, and frees the descriptor.
- Kqueue logic supports `EVFILT_JAILDESC`, filters selected `NOTE_JAIL_*` events, stores child/attach IDs in `kn_data`, and EOF/oneshot behavior on removal.
- `jaildesc_stat()`, `jaildesc_fill_kinfo()`, and `jaildesc_cmp()` expose descriptor status and comparison behavior.

## Dependencies And Integration
Integrates with the file descriptor table, file capabilities, jail core locking/lifetime APIs, poll/select, kqueue, `kinfo_file`, privilege checks, and prison descriptor lists.

## Risk Notes
Lock ordering is central: close may need to drop the descriptor lock, hold the prison, and then acquire jail locks before unlink/removal. Owning descriptors can remove jails on close, so descriptor lifetime directly affects jail lifecycle and must not race prison cleanup.

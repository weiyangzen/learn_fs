# File Research: sources/os/bsd/netbsd-src/sys/kern/tty_ptm.c

## Purpose

`tty_ptm.c` implements the pty multiplexor character device `/dev/ptm` and `/dev/ptmx`, allocating pty master/slave pairs and returning file descriptors and names to userland.

## Main Responsibilities

- Registers the `ptm_cdevsw` device switch, or a disabled no-op switch when `NO_DEV_PTM` is configured.
- Tracks pty master/slave major numbers.
- Finds a free pty minor and opens the master vnode.
- Grants/revokes the slave side by updating ownership/mode and revoking prior users.
- Allocates master and slave file descriptors for `TIOCPTMGET`.
- Supports `/dev/ptmx` open semantics using `EMOVEFD`.
- Provides hooks for alternate pty backends through `struct ptm_pty`.

## Allocation Flow

`pty_alloc_master()` reserves a file descriptor, finds a free pty, asks the active `ptm` backend for the master vnode, opens it as root credentials, initializes the file object, and affixes it to the process. Races for the same master retry when appropriate.

`pty_grant_slave()` obtains the slave vnode, applies backend-provided attributes if the filesystem is writable, revokes all existing users, and releases the stale vnode.

`pty_alloc_slave()` opens the slave vnode and affixes a second descriptor.

`ptmioctl(TIOCPTMGET)` combines these steps and fills `struct ptmget` with fds and pty names. `ptmopen()` handles `/dev/ptmx` by allocating a master and returning it via `l_dupfd`; the Linux-emulation minor also grants the slave immediately.

## Integration Notes

`ptmattach()` discovers the real pty cdev major numbers and installs the BSD compatibility backend when configured. `pty_sethandler()` lets another backend replace the active `ptm` handler.

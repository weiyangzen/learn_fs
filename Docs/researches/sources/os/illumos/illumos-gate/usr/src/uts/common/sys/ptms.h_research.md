# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ptms.h

## Role

`ptms.h` defines pseudo-terminal manager/subsidiary shared state, pty locking macros, kernel helper prototypes, owner data, and ptm ioctl command numbers.

## Kernel State

`struct pt_ttys` represents one manager/subsidiary pty pair:
- manager and subsidiary read queues.
- null message for subsidiary close.
- process/minor identifiers.
- reference count and state bits.
- condition variable and mutex.
- zone membership.
- real owner UID/GID.

State bits track pair lock, manager open, subsidiary open, and subsidiary tty status: `PTLOCK`, `PTMOPEN`, `PTSOPEN`, `PTSTTY`.

## Synchronization

The `PT_ENTER_READ`, `PT_ENTER_WRITE`, `PT_EXIT_READ`, and `PT_EXIT_WRITE` macros implement a reader/writer protocol over `pt_refcnt`:
- `-1` means writer.
- `0` means idle.
- positive values count readers.

The macros use `pt_lock` and `pt_cv`, with assertions on exit.

## Ioctls

The header defines ptm commands:
- `ISPTM`: verify manager fd.
- `UNLKPT`: unlock pty pair.
- `PTSSTTY`: set tty flag.
- `ZONEPT`: force pty into a zone.
- `OWNERPT`: set subsidiary owner/group.

`pt_own_t` carries owner UID/GID for owner-setting paths.

## Research Notes

This header is a pty control-plane ABI and internal synchronization contract. Zone ownership and `pt_refcnt` reader/writer semantics are the most important invariants.

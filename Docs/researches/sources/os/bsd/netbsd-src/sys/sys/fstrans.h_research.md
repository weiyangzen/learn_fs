# File Research: sources/os/bsd/netbsd-src/sys/sys/fstrans.h

Read completely: 73 lines.

## Purpose
Declares filesystem transaction and suspension APIs plus copy-on-write callback registration.

## Main Interfaces
- Suspend control flags: `SUSPEND_SUSPEND`, `SUSPEND_RESUME`.
- States: `FSTRANS_NORMAL`, `FSTRANS_SUSPENDED`, `FSTRANS_SUSPENDING`.
- Transaction APIs: `fstrans_init`, `fstrans_lwp_dtor`, `fstrans_start`, `fstrans_start_nowait`, `fstrans_start_lazy`, `fstrans_done`, `fstrans_held`, `fstrans_is_owner`.
- Mount lifecycle/state: `fstrans_mount`, `fstrans_unmount`, `fstrans_setstate`, `fstrans_getstate`.
- COW hooks: `fscow_establish`, `fscow_disestablish`, `fscow_run`.
- Public suspend/resume: `vfs_suspend`, `vfs_resume`.

## Dependencies And Integration
Includes `sys/mount.h`; implemented by VFS transaction code and used by filesystem operations, unmount, suspension, and buffer COW paths.

## Risks And Edge Cases
- Callers must pair `fstrans_start` and `fstrans_done`.
- Lazy/nowait starts differ during suspension.
- COW callbacks run in buffer write contexts and must obey locking/lifetime constraints.

## Filesystem Relevance
High. It is the public interface for safe filesystem suspension and transaction bracketing.

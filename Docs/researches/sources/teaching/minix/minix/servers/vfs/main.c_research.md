# File Research: sources/teaching/minix/minix/servers/vfs/main.c

This is the VFS server main loop and high-level dispatcher.

Key responsibilities:
- Starts SEF and worker threads.
- Receives messages from processes, PM, drivers, filesystem servers, DS, CLOCK, and kernel.
- Routes filesystem replies by VFS transaction ID.
- Routes block, character, and socket driver replies.
- Starts worker threads for normal VFS calls.
- Handles PM requests either immediately or via per-process worker serialization.
- Initializes process table, device/socket maps, vnode/vmnt/filp/select tables, PFS, and root filesystem.
- Supports live update by stopping/restarting worker threads at request/protocol-free states.

Main loop behavior:
- Yields to workers, sends queued FS work, receives/handles a message.
- FS replies are matched to worker threads with transaction IDs.
- PM messages go to `service_pm`.
- DS notifications start `ds_event`.
- CLOCK notifications expire timers for select.
- Kernel notifications dump stack traces.
- Normal syscalls call `handle_work(do_work)`.

Important functions:
- `handle_work`: starts a worker and handles FS callback deadlock rules.
- `do_reply`: delivers FS/VM replies to waiting workers.
- `do_work`: dispatches VFS calls through `call_vec`.
- `service_pm`: handles PM-originated state changes and postponed work.
- `service_pm_postponed`: runs exec/exit/coredump/unpause in target process context.
- `unblock`: reconstructs saved pipe/flock requests for revived processes.
- `do_init_root`: mounts PFS and boot ramdisk root.
- `lock_proc` / `unlock_proc`: fproc locking with worker suspension.
- `thread_cleanup`: clears FS callback state after worker completion.

Startup:
- Receives initial process table from PM.
- Subscribes to DS driver events.
- Maps boot-image services from RS public process table.
- Mounts PFS and root MFS on boot ramdisk.

Live update:
- Allows update only when workers are idle for request-free/protocol-free states.
- Reinitializes workers after live-update state transfer.

Notable behavior:
- VFS reserves special handling for FS callbacks to avoid deadlocks and uses a spare worker when service processes call back into VFS.

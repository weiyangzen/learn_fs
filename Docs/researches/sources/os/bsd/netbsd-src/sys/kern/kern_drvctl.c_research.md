# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_drvctl.c

Read completely: 685 lines.

Implements the `drvctl` driver-control pseudo-device, device-monitor event queue, ioctl handlers for suspend/resume/list/detach/rescan, plist command processing, and module glue.

`drvctl_init()` initializes the global event queue, mutex, condition variable, and select state. `devmon_insert()` is the devmon event insertion hook: it drops events when no process has drvctl open, adds the mandatory `"event"` string, bounds the FIFO to 64 entries by discarding the oldest event, wakes sleepers, and notifies poll/select waiters. `drvctlopen()` allocates a file descriptor and installs custom `drvctl_fileops` with `fd_clone()`, incrementing the open count. `drvctl_close()` decrements the open count and flushes queued events when the last opener closes.

Classic ioctls are handled under `KERNEL_LOCK`. `pmdevbyname()` suspends or resumes a named device recursively or by subtree. `listdevbyname()` lists direct children of a named device or root. `detachdevbyname()` finds a device through a writable deviter, checks parent detach notification support unless `XXXFULLRISK` is enabled, and calls `config_detach()`. `rescanbus()` validates bus/ifattr inputs, fills missing locators with `-1`, calls the bus attachment’s rescan hook for one or all interface attributes, and then runs deferred configuration.

Property-list commands currently support `"get-properties"`, which returns a device’s property dictionary. `drvctl_command()` copies in the command dictionary, validates command name and file access mode, calls the command handler, stores `"drvctl-error"` in the result dictionary, and copies results out. `drvctl_getevent()` requires read/write open mode, blocks interruptibly unless nonblocking, removes one queued event, copies it out, and releases it.

Module init attaches the devmon insertion hook, and loadable-module builds attach the device switch. Module fini refuses unload while open or while events remain, restores the previous devmon hook, detaches the device switch when applicable, and destroys state.

Risks and notes: event insertion silently releases and drops events when drvctl is unopened or the mandatory event string cannot be set. The event queue is lossy at depth 64. `drvctl_poll()` checks the queue without taking `drvctl_lock`, relying on broader select/poll conventions. `drvctl_command()` reports command-handler status inside the result dictionary but can overwrite the function return with copyout status. Detach is intentionally conservative unless built with `XXXFULLRISK`.

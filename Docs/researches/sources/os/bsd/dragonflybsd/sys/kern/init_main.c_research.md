# File Research: sources/os/bsd/dragonflybsd/sys/kern/init_main.c

## Summary
Core machine-independent boot orchestration for DragonFly BSD. It initializes process 0, executes ordered SYSINIT entries, creates process 1, mounts initial roots/devfs context, and starts `/sbin/init`.

## Main Responsibilities
- Defines static bootstrap objects for `proc0`, `lwp0`, `thread0`, session, process group, credentials, file descriptors, limits, and VM space.
- Implements `mi_proc0init()` for low-level CPU0 thread/LWP/proc linkage.
- Implements `mi_startup()` to sort and run linker-set SYSINIT records, including dynamically added SYSINITs.
- Initializes proc0/session/pgrp/credentials/sigacts/fd table/limits/vmspace in `proc0_init`.
- Creates and later schedules the init process through `create_init` and `kick_init`.
- Implements `start_init()` to set root directory, mount devfs, build user stack arguments, and try paths in `kern.init_path`.
- Initializes the user/kernel shared `kpmap` timing page metadata and per-CPU globaldata fields.

## Important Behavior
`mi_startup()` bubble-sorts SYSINIT entries by subsystem and order, marks completed entries with `SI_SPECIAL_DONE`, and restarts if `sysinit_add()` merges new entries.

`start_init()` obtains the root vnode from the boot mount, sets `fd_cdir` and `fd_rdir`, sets namecache roots, mounts devfs, creates a one-page user stack, and tries colon-separated init paths. It passes boot flags like `-s` when single-user mode is requested.

## Filesystem/VFS Signals
The file establishes the first process's root/cwd vnode references and namecache root, mounts devfs, and later executes init through `sys_execve`. Its early setup is foundational for all subsequent path lookup and VFS behavior.

## Risks
Boot ordering is critical. Incorrect SYSINIT subsystem/order values can run components before proc0, VM, clocks, root, or helper threads are ready. `start_init()` panics if no init path succeeds.

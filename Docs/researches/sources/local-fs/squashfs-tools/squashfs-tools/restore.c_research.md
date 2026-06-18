# File Research: sources/local-fs/squashfs-tools/squashfs-tools/restore.c

Signal-driven recovery coordinator for interrupted append/update operations. `restore_thrd()` waits for `SIGINT`, `SIGTERM`, or `SIGUSR1`; first interrupt warns that another interrupt will quit and restore, then later signals trigger cancellation.

The restore path disables progress/info output, cancels and joins the initial reader, worker readers, deflators, fragment processors, main thread, fragment deflators, order thread, and writer thread. It flushes the queues between stages so downstream threads idle before cancellation.

After all pipeline threads are stopped, it calls external `restorefs()`. `init_restore_thread()` starts the restore thread and returns its pthread handle.

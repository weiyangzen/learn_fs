# File Research: sources/os/linux/linux/fs/lockd/procfs.h

Purpose: Declares lockd procfs setup/teardown with no-op fallbacks when procfs is disabled.

Key contents:
- Under `CONFIG_PROC_FS`, declares `lockd_create_procfs()` and `lockd_remove_procfs()`.
- Otherwise provides inline stubs returning success and doing nothing.

Dependencies and integration:
- Included by lockd service/module initialization code.

Risk notes:
- Callers can unconditionally call procfs setup/teardown regardless of configuration.

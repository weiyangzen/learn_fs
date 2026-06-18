# File Research: sources/os/linux/linux/fs/dlm/Kconfig

## Role

Kconfig entries for the kernel Distributed Lock Manager.

## Configuration

`DLM`:

- Tristate option.
- Depends on `INET`.
- Depends on `SYSFS` and `CONFIGFS_FS`.
- Described as a general-purpose distributed lock manager for kernel or userspace applications.

`DLM_DEBUG`:

- Boolean option depending on `DLM`.
- Exposes per-lockspace debugfs files under a `dlm` directory.
- Debug output lists resources and locks known by the local node.

## Research Notes

This configuration establishes that DLM is networked and configfs/sysfs integrated, with optional debugfs visibility.

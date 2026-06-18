# File Research: sources/os/linux/linux-stable/fs/dlm/Kconfig

## Purpose

Defines kernel configuration options for the Distributed Lock Manager.

## Main Responsibilities

- Adds `menuconfig DLM` as a tristate option.
- Requires `INET`, `SYSFS`, and `CONFIGFS_FS`.
- Describes DLM as a general-purpose distributed lock manager for kernel or userspace applications.
- Adds `DLM_DEBUG`, dependent on `DLM`, to expose debugfs lockspace files showing resources and locks.

## Dependencies

- DLM build requires networking and configfs/sysfs infrastructure.
- Debug output depends on debugfs support through the DLM debug code.

# File Research: sources/os/linux/linux/fs/sysfs/Kconfig

Purpose: Kconfig option for sysfs support.

Key behavior:
- Defines `config SYSFS`, default `y`, visible under `EXPERT`.
- Selects `KERNFS`.
- Help text describes sysfs as a virtual filesystem exposing kernel objects, attributes, relationships, devices, drivers, and tunables.
- Notes that system agents and hotplug-style policy can rely on sysfs.
- Documents boot/root-device implications if sysfs is disabled and suggests embedded systems may disable it for space.

Dependencies:
- `KERNFS` is selected automatically when sysfs is enabled.

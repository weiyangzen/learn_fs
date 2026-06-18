# File Research: sources/os/linux/linux-stable/fs/sysfs/Kconfig

Purpose: Defines the kernel configuration option for sysfs.

Key responsibilities:
- Declares `CONFIG_SYSFS` as a boolean option, default enabled.
- Selects `KERNFS`.
- Documents sysfs as the virtual filesystem for kernel objects, attributes, and relationships.
- Notes userspace dependencies such as hotplug and root device discovery.

Important interactions:
- Sysfs can be disabled only under expert-style configuration, mainly for constrained embedded systems.
- The option supports driver core, block device discovery, and policy agents relying on sysfs.

Notable invariants and risks:
- Disabling sysfs can require specifying root devices by major/minor numbers and may break userspace agents that assume `/sys`.

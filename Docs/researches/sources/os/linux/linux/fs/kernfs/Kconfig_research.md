# File Research: sources/os/linux/linux/fs/kernfs/Kconfig

Kconfig symbol definition for kernfs.

Key responsibilities:
- Defines `KERNFS` as a boolean config symbol.
- Defaults `KERNFS` to disabled.
- Documents that kernfs should be selected by users rather than directly enabled.

Important interactions:
- Selected by subsystems that need kernfs-backed virtual filesystems, such as sysfs/cgroup-style hierarchies.

Invariants and risks:
- Direct user selection is intentionally avoided; dependency owners must select it when needed.

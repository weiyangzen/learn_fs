# File Research: sources/os/linux/linux-stable/fs/kernfs/Kconfig

## Purpose

Defines the internal `KERNFS` configuration symbol.

## Behavior

`KERNFS` is a boolean symbol with default `n`. The comment states it should be selected by users rather than enabled directly, matching kernfs being infrastructure for pseudo-filesystems such as sysfs/cgroupfs rather than a standalone user option.

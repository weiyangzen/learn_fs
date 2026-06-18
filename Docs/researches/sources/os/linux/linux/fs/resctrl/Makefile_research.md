# File Research: sources/os/linux/linux/fs/resctrl/Makefile

Build rules for the resctrl filesystem.

Key behavior:
- When `CONFIG_RESCTRL_FS` is enabled, builds:
  - `rdtgroup.o`
  - `ctrlmondata.o`
  - `monitor.o`
- When `CONFIG_RESCTRL_FS_PSEUDO_LOCK` is enabled, builds:
  - `pseudo_lock.o`
- Adds `-I$(src)` to `monitor.o` so `define_trace.h` recursive include requirements are satisfied.

Research notes:
- This file only controls compilation; it contains no runtime logic.

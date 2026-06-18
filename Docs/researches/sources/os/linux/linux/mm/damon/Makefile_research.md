# File Research: sources/os/linux/linux/mm/damon/Makefile

Build rules for DAMON objects.

Behavior:
- Always builds `core.o` into `obj-y`.
- Adds `ops-common.o` plus `vaddr.o` when `CONFIG_DAMON_VADDR` is enabled.
- Adds `ops-common.o` plus `paddr.o` when `CONFIG_DAMON_PADDR` is enabled.
- Adds sysfs pieces for `CONFIG_DAMON_SYSFS`.
- Adds `modules-common.o` plus `reclaim.o`, `lru_sort.o`, or `stat.o` for the corresponding DAMON modules.

Notable detail: both virtual and physical address operations share `ops-common.o`, and module-style DAMON consumers share `modules-common.o`.

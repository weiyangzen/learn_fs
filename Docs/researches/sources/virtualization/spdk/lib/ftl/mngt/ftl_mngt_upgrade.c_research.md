# File Research: sources/virtualization/spdk/lib/ftl/mngt/ftl_mngt_upgrade.c

Wraps layout upgrade into management-process steps. `ftl_mngt_layout_upgrade()` calls a process that repeatedly selects the next region requiring upgrade, runs the corresponding region upgrade, persists the superblock, and continues until done.

Important behavior:
- Allocates per-region upgrade context according to descriptor `ctx_size`.
- `region_upgrade_cb()` frees upgrade context, stores the superblock blob area on success, then advances.
- `layout_upgrade()` handles `CONTINUE`, `DONE`, and `FAULT` outcomes from `ftl_layout_upgrade_init_ctx()`.
- On completion it verifies/dumps upgraded layout via `ftl_upgrade_layout_dump()`.

Risk:
- Upgrade context ownership is split across async region callbacks and parent loop; careful cleanup avoids leaks but requires region upgrades to honor callback contracts.

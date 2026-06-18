# File Research: sources/os/linux/linux/fs/verity/init.c

## Purpose
Initializes the fs-verity subsystem and provides rate-limited logging.

## Main Functions
- `fsverity_init_sysctl()`: registers `/proc/sys/fs/verity` sysctls when enabled; includes `require_signatures` when builtin signatures are configured.
- `fsverity_msg()`: rate-limited printk helper with optional filesystem/inode context.
- `fsverity_init()`: late initcall that validates hash algorithms, initializes info cache, workqueue, sysctl, signature keyring, and BPF kfunc support.

## Important Design Points
- Logging is globally rate-limited to avoid flooding on repeated verification failures.
- `CREATE_TRACE_POINTS` is defined here for fs-verity trace events.
- Initialization panics indirectly if critical caches/workqueues/keyrings cannot be created.

## Cross-File Relationships
- Calls init functions from `hash_algs.c`, `open.c`, `verify.c`, `signature.c`, and `measure.c`.
- Sysctl variable `fsverity_require_signatures` is defined in `signature.c`.

## Risks / Review Notes
- `late_initcall` ordering assumes dependent kernel subsystems are ready.
- Sysctl table is empty unless builtin signature support contributes an entry.

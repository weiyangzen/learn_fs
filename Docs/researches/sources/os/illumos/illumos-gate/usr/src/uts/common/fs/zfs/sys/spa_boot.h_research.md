# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/spa_boot.h

This small header declares boot-time SPA support hooks.

Core API surface:
- `spa_get_bootprop()` retrieves a named boot property string.
- `spa_free_bootprop()` releases a returned property value.
- `spa_arch_init()` performs architecture-specific boot SPA initialization.

Risk-sensitive invariants:
- Returned boot property memory must be released through the matching SPA helper.
- This interface is intentionally minimal and depends only on nvpair-facing boot configuration.

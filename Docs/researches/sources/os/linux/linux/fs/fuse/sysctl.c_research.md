# File Research: sources/os/linux/linux/fs/fuse/sysctl.c

Registers `/proc/sys/fs/fuse` tunables for global FUSE request sizing and timeout limits.

Key entry points:
- `fuse_sysctl_register()`
- `fuse_sysctl_unregister()`

Tunables:
- `max_pages_limit` maps to `fuse_max_pages_limit`, min 1, max 65535.
- `default_request_timeout` maps to `fuse_default_req_timeout`, min 0, max 65535.
- `max_request_timeout` maps to `fuse_max_req_timeout`, min 0, max 65535.

Dependencies and integration:
- Uses `register_sysctl()` with `proc_douintvec_minmax`.
- Bounds match `fuse_init_out` protocol fields that are `u16`.

Risks and invariants:
- Register failure returns `-ENOMEM`.
- Unregister clears the global table header after `unregister_sysctl_table()`.

# File Research: sources/os/linux/linux-stable/fs/coda/sysctl.c

This file registers Coda runtime tunables under the `coda` sysctl directory.

Key responsibilities:
- Exposes `timeout`, `hard`, and `fake_statfs` sysctl entries.
- Implements `coda_sysctl_init()` and `coda_sysctl_clean()`.

Important control flow:
- `coda_sysctl_init()` registers the table only if `fs_table_header` is not already set.
- `coda_sysctl_clean()` unregisters and clears the header.

Dependencies:
- Uses globals declared through `coda_int.h`: `coda_timeout`, `coda_hard`, and `coda_fake_statfs`.

Risks and invariants:
- `timeout` and `hard` are writable by normal root-style sysctl permissions.
- `fake_statfs` is mode `0600`, making it more restricted.
- Cleanup is idempotent around the stored header pointer.

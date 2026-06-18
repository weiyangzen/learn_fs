# File Research: sources/local-fs/f2fs-tools/fsck/inject.h

Purpose: declares the public interface and option carrier for `inject.f2fs`.

Key contents:
- Includes standard integer/limits headers plus `f2fs_fs.h` and `fsck.h`.
- Defines `struct inject_option`, which stores selected member name, array index, numeric/string replacement value, target nid/block, selected superblock/checkpoint/NAT/SIT pack, dot/dotdot mode, and boolean selectors for SSA, node, and dentry injection.
- Exposes `inject_usage()`, `inject_parse_options()`, and `do_inject()`.

Role in the group:
- `main.c` allocates a static `inject_option`, initializes sentinel values, passes it to `inject_parse_options()`, and stores it in `c.private`.
- `inject.c` consumes the struct to dispatch and perform mutations.

Risk notes:
- `idx` is unsigned but initialized with `-1` in `main.c`, relying on `UINT_MAX` as the sentinel for “auto index” in several injection paths.

# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/inst_sync.c

## Purpose

`inst_sync.c` implements the loadable `inst_sync` syscall used to write kernel device instance-number assignments to stable storage.

Read completely: 372 lines.

## Main Responsibilities

- Registers a two-argument syscall module through `_init()`, `_info()`, and `_fini()`.
- Validates privilege and flags in `in_sync_sys()`.
- Serializes access to instance data with `e_ddi_enter_instance()` / `e_ddi_exit_instance()`.
- Avoids unnecessary writes when instance data is clean unless forced.
- Creates a new instance file without overwriting an existing file.
- Walks the kernel instance tree and writes permanent instance bindings.
- Flushes and fsyncs the created file.
- Removes the created file on error.

## Syscall Behavior

Userland sees `int inst_sync(pathname, flags)`.

Supported flags are:

- `INST_SYNC_IF_REQUIRED`: write only if instance information changed.
- `INST_SYNC_ALWAYS`: write even if instance information is clean.

The syscall requires `secpolicy_sys_devices()`. `inst_sync_disable` can make the syscall a no-op for debugging/testing.

If instance data is clean and the caller did not force a write, the syscall returns `EALREADY`.

## File Creation And Writing

`in_sync_sys()` opens the pathname with `vn_open()` using `FCREAT`, mode `0444`, and `CRCREAT`, explicitly refusing overwrite. `EISDIR` is translated to `EACCES`.

`in_write_instance()` wraps the vnode in a small local buffered `File` abstraction, writes a warning header, then walks the instance tree.

`in_write()`, `in_fputs()`, `in_fflush()`, and `in_fclose()` implement minimal kernel-side buffered output using `vn_rdwr()`, `VOP_FSYNC()`, `VOP_CLOSE()`, and `VN_RELE()`.

## Instance Tree Format

`in_walktree()` recursively walks `in_node_t` children. For each node with drivers, it builds a device path component using `node` or `node@unit-address`, then writes one line for each driver binding whose state is `IN_PERMANENT`.

It skips provisional and unknown assignments to avoid duplicate or `-1` instances.

Output lines encode:

- quoted device path
- instance number
- quoted driver name

## Important Invariants

- Only one instance sync runs at a time.
- The file is only marked clean after a full successful write, flush, and close.
- Partial files are removed on error.
- The path-building buffer is global/shared during recursion and must be treated carefully.
- Instance state must be permanent before it is persisted.

## Research Relevance

This file touches filesystem behavior through kernel-side file creation, write, fsync, close, and removal. It is also relevant to device-tree persistence, which affects stable device naming and therefore storage device identity across reboot.

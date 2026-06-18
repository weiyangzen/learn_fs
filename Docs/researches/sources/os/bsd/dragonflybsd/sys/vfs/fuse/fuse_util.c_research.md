# File Research: sources/os/bsd/dragonflybsd/sys/vfs/fuse/fuse_util.c

Provides utility functions for debugging, FUSE header construction, forget requests, reply length auditing, and opcode name lookup.

`fuse_hexdump` prints bytes only when `fuse_debug` is enabled. `fuse_fill_in_header` populates `struct fuse_in_header` with length, opcode, unique ID, node ID, uid, gid, and pid.

`fuse_forget_node` builds a `FUSE_FORGET` request with `struct fuse_forget_in`, sends it through `fuse_ipc_tx_noreply`, and drops the IPC after successful send.

`fuse_audit_length` validates successful userspace reply payload lengths against the original opcode. It requires exact lengths for lookup/getattr/setattr/open/write/statfs/init/opendir/create and zero lengths for many mutation operations; read, readdir, and readlink allow bounded variable lengths. Unsupported or unimplemented operations return failure; invalid opcodes panic.

`fuse_get_ops` maps all known ABI opcodes to string names for debug logging and panics on invalid opcode.

Important dependencies: `fuse_abi.h` structures and opcodes, IPC buffer helpers from `fuse.h`, and debug macros.

Notable risks or research hooks: reply auditing ignores older `FUSE_COMPAT_*` sizes by design. Many newer operations intentionally return unsupported in the audit switch, matching partial FUSE implementation coverage.

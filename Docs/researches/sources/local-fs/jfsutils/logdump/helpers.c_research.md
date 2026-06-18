# File Research: sources/local-fs/jfsutils/logdump/helpers.c

Provides minimal helper substitutes for fsck/logredo routines needed by `jfs_logdump` outside the full fsck environment.

Important functions:
- `alloc_wrksp(...)`: allocates heap workspace, rounding the requested size upward. It initializes the output pointer to `NULL`, calls `malloc`, and currently returns `0` even if allocation fails.
- `v_fsck_send_msg(...)`: formats a message from `msg_defs[msg_num]` using varargs, appends source file and line detail, and prints to stdout.

Dependencies:
- Uses `fsck_message.h`, `jfs_types.h`, and external message globals such as `msg_defs`.
- Exists to satisfy logredo/fsck-linked code paths used by log dumping.

Notable risk: `alloc_wrksp` does not set an error return on `malloc` failure, so callers must not assume nonzero return means allocation failure.

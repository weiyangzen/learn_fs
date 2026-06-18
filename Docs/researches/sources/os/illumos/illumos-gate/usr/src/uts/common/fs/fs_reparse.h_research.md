# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/fs_reparse.h

## Role

Declares shared kernel/user interfaces and constants for illumos filesystem reparse-point support.

## Main Behavior

- Defines reparse marker tokens such as `FS_REPARSE_TAG_STR`, token delimiters, `MAXREPARSELEN`, and the reparsed door path `/var/run/reparsed_door`.
- Defines `REPARSED_DOORCALL_MAX_RETRY` and SMF service name `REPARSED`.
- Declares `reparsed_door_res_t`, the door response structure shared across 32-bit userland and 64-bit kernel code. Its `res_len` is explicitly `int` for ABI compatibility.

## API Surface

- Common nvlist helpers: `reparse_init()`, `reparse_free()`, `reparse_parse()`, and `reparse_validate()`.
- Kernel-only functions: `reparse_kderef()` and `reparse_vnode_parse()`.
- Userland-only functions: `reparse_add()`, `reparse_remove()`, `reparse_unparse()`, `reparse_create()`, `reparse_delete()`, and `reparse_deref()`.

## Dependencies And Interactions

- Uses kernel `sys/nvpair.h` under `_KERNEL` or `_FAKE_KERNEL`; uses `libnvpair.h` for userland.
- Implemented in part by `fs_subr.c` for kernel vnode parsing and door upcall dereferencing.

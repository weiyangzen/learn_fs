# sources/user-network-fs/samba/source3/libsmb/libsmb_compat.c

Purpose: provides the old global libsmbclient API (`smbc_open`, `smbc_read`, `smbc_opendir`, etc.) on top of the newer context/callback based `SMBCCTX` API. It keeps source compatibility for applications that use integer handles instead of `SMBCFILE *`.

Important APIs/types: `struct smbc_compat_fdlist` maps synthetic integer descriptors to `SMBCFILE *`. Static globals include `statcont` for the active context, initialization flag, deterministic descriptor counter, and in-use/available descriptor lists. `smbc_init()` creates and initializes the default context; `smbc_set_context()` swaps in a caller-owned initialized context. `find_fd()`, `add_fd()`, and `del_fd()` manage descriptor indirection.

Control flow and state: most exported functions look up an `SMBCFILE *` from the synthetic fd and call the corresponding function pointer retrieved from `statcont`. Open/creat/opendir allocate a descriptor after the underlying context operation succeeds; close/closedir remove the descriptor before delegating close. Extended attribute `f*` calls validate the fd and often operate on `file->fname`.

Dependencies and integration: this file depends heavily on getters in `libsmb_setget.c` and implementations installed by `smbc_new_context()`. It exposes legacy ABI while sharing all real network behavior with `libsmb_file.c`, `libsmb_dir.c`, `libsmb_stat.c`, and printjob code.

Risks: all compatibility state is process-global and not protected here by per-call locks; callers needing thread isolation should use explicit contexts. `smbc_close()` deletes the fd before closing, so close failure still invalidates the compatibility descriptor. `smbc_open_print_job()` returns `file->cli_fd` directly instead of a compatibility fd, which is legacy behavior but easy to misuse. Test signals: init idempotence, fd reuse from the available list, `FD_SETSIZE` exhaustion, bad fd xattr behavior, and wrappers calling overridden context callbacks.

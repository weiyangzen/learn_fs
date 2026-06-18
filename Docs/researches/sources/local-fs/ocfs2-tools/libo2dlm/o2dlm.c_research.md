# File Research: sources/local-fs/ocfs2-tools/libo2dlm/o2dlm.c

Implements the userspace `libo2dlm` locking API for OCFS2 tooling. It supports two backends: classic `dlmfs` lock files and, when built with `HAVE_FSDLM`, filesystem DLM via dynamically loaded `libdlm_lt.so.3`.

Key structures are `o2dlm_ctxt`, `o2dlm_lock_res`, and `o2dlm_lock_bast`. Contexts maintain hash tables for held locks and BAST callbacks, a domain path/name, and optional fsdlm library/lockspace handles. A random hidden context lock name is generated from `/dev/urandom` and held for the context lifetime to keep the domain alive.

Classic mode validates the `dlmfs` mount by `statfs()` against `USER_DLMFS_MAGIC`, creates/checks a domain directory, represents locks as files opened `O_RDONLY` for PR or `O_RDWR` for EX, and uses nonblocking open for trylock. LVB reads/writes use `lseek()` plus file I/O on the lock file. Teardown closes all locks, unregisters BAST entries, unlinks remaining lock files where possible, and removes the domain directory unless busy.

fsdlm mode resolves `dlm_create_lockspace`, `dlm_release_lockspace`, `dlm_ls_lock_wait`, and `dlm_ls_unlock_wait` with `dlopen`/`dlsym`. It maps OCFS2 PR/EX/TRYLOCK to DLM lock modes and flags, always requests LVB support, translates common errno/status values into `O2DLM_ET_*`, and stores LVB contents in each lock resource’s `dlm_lksb`.

Public API functions validate arguments and reserved names, then dispatch by backend: `o2dlm_initialize`, `o2dlm_destroy`, `o2dlm_lock`, `o2dlm_lock_with_bast`, `o2dlm_unlock`, `o2dlm_drop_lock`, `o2dlm_read_lvb`, `o2dlm_write_lvb`, and `o2dlm_process_bast`.

Notable behavior: lock IDs starting with `.` are reserved for internal context locks; recursive lock attempts are rejected; classic BAST support is probed lazily; `o2dlm_unlock()` removes lock/BAST bookkeeping before backend unlock and treats busy-lock unlock as nonfatal.

# sources/user-network-fs/nfs-utils/support/misc/ucred.c

Purpose: credential utility routines for export-aware UID/GID handling and temporarily swapping the process effective credentials.

Important APIs and functions: `nfs_ucred_squash_groups()` rewrites root group IDs to the export anonymous GID under root-squash. `nfs_ucred_reload_groups()` reloads supplementary groups for a credential UID using `getpwuid_r()` and `getgrouplist()`, then reapplies squash policy. `nfs_ucred_swap_effective()` captures the current effective credentials and sets effective UID/GID/groups to a supplied `nfs_ucred`.

Control flow: effective credential capture uses `getgroups()`, heap allocation, `geteuid()`, and `getegid()`. Swap first raises effective UID to 0, installs supplementary groups, changes effective GID, then changes effective UID; error paths attempt to restore GID and groups from the saved credential.

State and persistence: no durable state. It mutates process effective credentials and allocates/free group arrays owned by `struct nfs_ucred`.

Dependencies and integration: depends on `exportfs.h` export flags, `nfs_ucred.h` ownership helpers, libc password/group APIs, `setresuid()`, `setresgid()`, `setgroups()`, and `xlog`. It is used by NFS server utilities that need filesystem operations under client/export credentials.

Risks: changing process credentials is global to the thread/process security context and is risky in multithreaded use. `alloca()` uses the system password-buffer size and can still allocate 16 KiB on stack by default. Partial failures during credential swap may leave credentials only partly restored. `nfs_ucred_reload_groups()` returns early for anonymous users under squash policy, which preserves the current group set by design but should be verified against caller expectations.

Test signals: run as root in a controlled test for successful swap/restore, root squash group replacement, all-squash anonymous handling, unknown UID, large group lists, and failure injection around `setgroups()`/`setresgid()`/`setresuid()`.

# sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_sys.c

Purpose: `pvfs_sys.c` wraps POSIX filesystem syscalls so PVFS can optionally override `EACCES` after ACL checks while reducing symlink-attack risk. It is the low-level bridge for open, unlink, rename, mkdir, rmdir, chmod, and fchmod operations.

Important APIs, types, and functions: Public wrappers are `pvfs_sys_open`, `pvfs_sys_unlink`, `pvfs_sys_rename`, `pvfs_sys_mkdir`, `pvfs_sys_rmdir`, `pvfs_sys_fchmod`, and `pvfs_sys_chmod`. Local state is `struct pvfs_sys_ctx`, which holds root-privilege state, original working directory, and original cwd stat. Helpers include `pvfs_sys_pushdir_destructor`, `pvfs_sys_chdir_nosymlink`, `pvfs_sys_pushdir`, `pvfs_sys_fchown`, `pvfs_sys_chown`, and `contains_symlink`.

Control flow: Each wrapper first attempts the normal syscall. If it succeeds, override is disabled, or failure is not `EACCES`, the result is returned. Otherwise `pvfs_sys_pushdir` gains root privileges, records cwd, safely changes to the path's parent while checking intermediate symlinks, rewrites the operand to a basename, and retries. Creation paths chown newly created files/directories back to the original uid. Rename additionally checks the destination for symlink behavior before and after the privileged rename.

State and persistence behavior: Wrappers mutate filesystem objects and ownership/modes but do not store Samba metadata. Temporary privilege and cwd state is talloc-scoped and restored by destructor; restoration panics if the cwd identity changed unexpectedly.

Dependencies and integration points: It depends on Samba `root_privileges`, POSIX open/unlink/rename/mkdir/rmdir/chmod APIs, `O_NOFOLLOW`/`O_DIRECTORY` where available, and the `allow_override` flag computed by higher-level PVFS access logic.

Risks: Process-wide `chdir` during privileged operations is inherently delicate in evented servers. Systems without `O_NOFOLLOW` or `O_DIRECTORY` are less protected. Symlink detection is platform-specific and maps several OS-specific errno values. Incorrect caller use before ACL checks would be a privilege bug.

Test signals: Cover normal and override paths for each wrapper, ownership after privileged create/mkdir, symlink-in-parent rejection, destination symlink rejection on rename, cwd restoration, disabled override, and behavior on platforms lacking no-follow flags.

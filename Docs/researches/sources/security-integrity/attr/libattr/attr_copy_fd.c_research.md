## sources/security-integrity/attr/libattr/attr_copy_fd.c

Purpose: copy extended attributes between open file descriptors.

`attr_copy_fd` lists source fd xattrs, grows name/value buffers on `ERANGE`, filters each name, gets values, and writes them to the destination fd. It reports per-attribute errors through `error_context` and tolerates unavailable xattr support on listing. State is local buffers with stack defaults and heap growth. Dependencies are `flistxattr`, `fgetxattr`, `fsetxattr`, gettext, and `attr_copy_check_permissions`. Risks include partial-copy semantics, delayed aggregate ENOTSUP reporting, no rollback, large xattr memory growth, and check callback side effects. Tests should cover small/large values, unsupported destination filesystems, ACL filtering, and ENOSYS/ENOTSUP handling.

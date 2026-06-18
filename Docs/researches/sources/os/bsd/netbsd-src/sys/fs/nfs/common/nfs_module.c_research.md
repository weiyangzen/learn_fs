# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfs_module.c

This is a minimal NetBSD module wrapper for `nfs_common`.

Key contents:
- Declares `MODULE(MODULE_CLASS_MISC, nfs_common, NULL)`.
- `nfs_common_modcmd()` accepts `MODULE_CMD_INIT` and `MODULE_CMD_FINI`, returning success.
- Other module commands return `ENOTTY`.

Important dependencies:
- This is NetBSD module framework glue, separate from FreeBSD-style `DECLARE_MODULE` code present in some imported files.

Risks and notes:
- No initialization logic lives here; actual common initialization is in the imported/ported common module paths.

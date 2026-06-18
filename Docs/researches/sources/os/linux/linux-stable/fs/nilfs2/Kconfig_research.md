# File Research: sources/os/linux/linux-stable/fs/nilfs2/Kconfig

Purpose: declares the kernel configuration option for NILFS2 filesystem support.

Key structures and state:
- Defines `CONFIG_NILFS2_FS` as a tristate option named “NILFS2 file system support”.
- Selects `BUFFER_HEAD`, `CRC32`, and `LEGACY_DIRECT_IO`.

Major logic:
- Help text describes NILFS2 as a log-structured filesystem with continuous checkpointing and mountable read-only snapshots.
- Documents that atime, extended attributes, and POSIX ACLs are not supported yet.
- Notes the module name is `nilfs2`.

Concurrency and lifetime:
- No runtime code; controls build inclusion.

Important dependencies:
- Build-time dependency selection ensures required buffer-head, CRC, and legacy direct-I/O support are available.

Risk/edge cases:
- Feature support described here constrains expectations for VFS features such as xattrs and ACLs.

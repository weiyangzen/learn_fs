# File Research: sources/local-fs/ocfs2-tools/mount.ocfs2/mount_constants.h

Compatibility header for Linux `mount(2)` flag constants.

It conditionally defines common flags such as `MS_RDONLY`, `MS_NOSUID`, `MS_NODEV`, `MS_NOEXEC`, `MS_REMOUNT`, `MS_NOATIME`, `MS_RELATIME`, `MS_STRICTATIME`, bind/move/recursive flags, and legacy mount magic values when the platform headers do not provide them.

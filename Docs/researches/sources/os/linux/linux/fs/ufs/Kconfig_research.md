# File Research: sources/os/linux/linux/fs/ufs/Kconfig

Purpose: kernel configuration for Linux UFS filesystem support.

Key contents:
- `UFS_FS`: tristate UFS filesystem support, depends on `BLOCK`, selects `BUFFER_HEAD`; help states default support is read-only and module name is `ufs`.
- `UFS_FS_WRITE`: optional dangerous experimental write support depending on `UFS_FS`.
- `UFS_DEBUG`: optional debug logging depending on `UFS_FS`.

Integration:
- Controls compilation of the UFS module and debug macro behavior used throughout UFS sources.
- User-facing help points to `Documentation/admin-guide/ufs.rst`.

Risks and invariants:
- Write support is explicitly labeled dangerous/experimental.
- UFS2 is described as read-only supported in help text.

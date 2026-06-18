# File Research: sources/os/linux/linux/fs/vboxsf/vboxsf_wrappers.c

## Purpose
Wraps VirtualBox HGCM shared-folder service calls in Linux-friendly functions used by the vboxsf filesystem.

## Main Functions
- Connection:
  - `vboxsf_connect()`: connects to `VBoxSharedFolders` HGCM service and stores client id.
  - `vboxsf_disconnect()`: disconnects from the service.
  - `vboxsf_call()`: common HGCM call wrapper converting VirtualBox status to Linux errno.
- Folder mapping:
  - `vboxsf_map_folder()` / `vboxsf_unmap_folder()`: map and unmap host shared folder roots.
- Object operations:
  - `vboxsf_create()`, `vboxsf_close()`, `vboxsf_remove()`, `vboxsf_rename()`.
  - `vboxsf_read()` / `vboxsf_write()`: perform handle-based I/O and update byte counts.
  - `vboxsf_dirinfo()`: list directory entries and converts `VERR_NO_MORE_FILES` to positive `1`.
  - `vboxsf_fsinfo()`: get/set file or volume information.
  - `vboxsf_readlink()` / `vboxsf_symlink()`.
  - `vboxsf_set_utf8()` / `vboxsf_set_symlinks()`.

## Important Design Points
- All host calls use a fixed requestor mask `SHFL_REQUEST`.
- Parameters are explicitly typed as 32-bit, 64-bit, kernel linear address input/output, or optional zero address.
- `vboxsf_create()` may return success even when a file was not opened or created; callers must inspect `create_parms->handle` and `result`.
- `vboxsf_dirinfo()` returns `0` for data, `1` for end-of-directory, or negative errno for failure.

## Cross-File Relationships
- Consumes ABI structs from `shfl_hostintf.h`.
- Called by all higher-level vboxsf VFS code.
- Relies on VirtualBox guest utilities from `linux/vbox_utils.h` and status mapping from `linux/vbox_err.h`.

## Risks / Review Notes
- Host status and Linux errno are both relevant in some cases; `map_folder()` and `dirinfo()` explicitly inspect raw status.
- Pointer size fields must match actual SHFL buffer sizes to avoid malformed HGCM calls.
- Global `vboxsf_client_id` assumes serialized setup/teardown from `super.c`.

# sources/user-network-fs/libsmb2/lib/dreamcast/vfs.h

Purpose: Declares the Dreamcast/KallistiOS SMB VFS lifecycle API.

Important APIs/functions: `kos_smb_init(const char *url)` initializes libsmb2, connects to an SMB URL, and registers `/smb`; `kos_smb_shutdown(void)` unregisters and tears down the connection.

Control flow: Header only; callers invoke init before VFS use and shutdown when the mount is no longer needed.

State/persistence: The implementation uses global state, but the header does not expose handles, so only one implicit mount/context is supported.

Dependencies/integration: Include guard `__KOS_SMB_VFS_H__`. Intended for Dreamcast/KOS consumers that link `vfs.c` and libsmb2.

Risks: The API has no context handle or idempotency contract, so repeated init/shutdown behavior depends on implementation details. It does not expose error strings beyond the integer return from init.

Test signals: Compile with KOS toolchain; verify callers can include the header from C and that init/shutdown lifecycle tests cover success, parse failure, connect failure, and repeated calls.

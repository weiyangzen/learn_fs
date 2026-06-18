# File Research: sources/os/linux/linux/fs/smb/client/ioctl.c

## Purpose
Implements CIFS/SMB VFS ioctl dispatch for filesystem flags, server-side copy, query info, mount/session information, snapshots, encryption-key debug dumping, notifications, integrity/compression controls, and forced shutdown.

## Main Interfaces
- `cifs_ioctl()` is the exported ioctl dispatcher.
- `cifs_ioctl_query_info()` converts a dentry path to UTF-16 and calls dialect query-info ioctl support.
- `cifs_ioctl_copychunk()` copies an entire source file to the destination through server-side copychunk.
- `smb_mnt_get_fsinfo()` and `smb_mnt_get_tcon_info()` copy mount/tcon data to userspace.
- `cifs_shutdown()` sets mount forced-shutdown state.
- `cifs_dump_full_key()` exports SMB3 encryption keys for privileged debugging.

## Control Flow
`cifs_ioctl()` obtains an XID, traces the command, checks whether a file handle is required, and dispatches by ioctl command. Most commands call server dialect operations when present and otherwise return `-EOPNOTSUPP`, `-ENOTTY`, or validation errors. Copychunk validates write access and source filesystem identity, shutdown validates `CAP_SYS_ADMIN` and supported flags, and key dump validates encryption state plus key-buffer sizing.

## State And Synchronization
Uses tcon links and session references while copying mount data or key material. `cifs_dump_full_key()` can search all TCP sessions under `cifs_tcp_ses_lock`, protects session status with `ses_lock`, increments the session refcount while using a found session, and releases it afterward.

## Integration Points
Dispatches to dialect callbacks including `ioctl_query_info`, `set_compression`, `set_integrity`, `enum_snapshots`, and `notify`. Uses mount write accounting for copychunk and tracepoints for ioctl/shutdown observability.

## Notable Behaviors
- `FS_IOC_GETFLAGS` can expose legacy Unix extension flags or compression status.
- `FS_IOC_SETFLAGS` only attempts compression today.
- `CIFS_DUMP_KEY` handles older AES-128 debug format; `CIFS_DUMP_FULL_KEY` handles variable key sizes.
- `CIFS_IOC_SHUTDOWN` supports logflush/nologflush-style shutdown by setting `CIFS_MOUNT_SHUTDOWN`.

## Risks And Review Focus
- Key dumping is intentionally privileged but exposes sensitive session keys; any expansion should preserve capability checks and buffer validation.
- User-copy paths must keep structure sizing and `copy_to_user()`/`copy_from_user()` failures exact.
- Copychunk assumes both files are CIFS by comparing ioctl operation tables.

# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb_usr.c

## Scope

This file implements the kernel side of netsmb user ioctls for session, tree, file handle, I/O, named pipe transaction, print job, IOD, and password-key operations.

## APIs And Behavior

- `smb_usr_get_ssnkey()` returns the active session key to userland for RPC encryption use.
- `smb_usr_xnp()` handles transact-named-pipe using SMB2 IOCTL `FSCTL_PIPE_TRANSCEIVE` or SMB1 transaction2 named pipe.
- `smb_cpdatain()` copies ioctl payload data into an mbchain.
- `smb_usr_rw()` converts SMBIOC read/write arguments into a one-element `uio` and calls `smb_rwuio()`.
- `smb_usr_ntcreate()` opens a named file on the current share and stores the resulting file handle in the device state.
- `smb_usr_printjob()` creates a print queue file, validating the print job title against invalid SMB filename characters.
- `smb_usr_closefh()` closes and releases the current file handle.
- `smb_usr_get_ssn()` finds or creates a VC/session, validates requested ownership against caller credentials, optionally marks the device as IOD, and waits for active state on find.
- `smb_usr_drop_ssn()` releases or kills the current VC and any attached share.
- `smb_usr_get_tree()` finds or connects a share and returns actual share type.
- `smb_usr_drop_tree()` releases or kills the current share.
- `smb_usr_iod_ioctl()` handles userland IOD state-machine calls for connect, negotiate, session setup, work, idle, and reconnect failure.
- `smb_usr_ioctl()` serializes ioctls per device and dispatches all SMBIOC commands.

## State And Dependencies

- Operates on `smb_dev_t` fields `sd_vc`, `sd_share`, `sd_fh`, `sd_flags`, and `sd_level`.
- Depends on connection/session/share lookup, SMB1/SMB2 request functions, mchain, credential helpers, password-key ioctls, and IOD functions.

## Risks And Invariants

- All per-device ioctl handlers assume serialization via `NSMBFL_IOCTL`.
- Reconnect generation mismatches return `ESTALE` for open file handles.
- Tree-connect structures may contain cleartext passwords and are zeroed before free.
- IOD ownership is enforced by `NSMBFL_IOD` and `vcp->iod_thr`.

# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb_dev.c

## Purpose
Implements the `/dev/nsmb` pseudo-device driver used by userland SMB tooling and `smbiod` to create sessions, issue ioctls, duplicate device state, and hand mounted smbfs a referenced share.

## Key Elements
Module initialization sets up soft-state storage, device locks, the connection manager, the password keychain, and zone callbacks, then installs the kernel driver. `_fini` refuses unload while active VCs or stored password hashes remain, removes the module, deletes the zone key, and tears down shared state.

The kernel driver exposes clone open/close/ioctl operations. `nsmb_open` allocates a unique minor soft-state instance, marks it open, records the caller zone, and initializes the instance lock. `nsmb_ioctl` validates the soft-state instance, open flag, and same-zone access, then dispatches to `smb_usr_ioctl`. `nsmb_close` releases attached file handle, share, and VC references; if the instance belongs to an IOD, closing it disconnects the VC because no reader remains.

Attach/detach create/remove the `nsmb` character minor node and discover major device numbers for TCP/TCP6 transport opens. Non-kernel wrappers map the same open/close/ioctl behavior for `libfknsmb`. `smb_usr_dup_dev` copies VC/share references from another nsmb file descriptor, incrementing reference counts. `smb_dev2share` validates an nsmb descriptor and returns a held share pointer for mount setup.

## Dependencies
Depends on illumos driver/module/DDI soft-state APIs, zones, credentials, file descriptor lookup, vnode device numbers, transport major lookup, connection/reference APIs, password-keychain lifecycle, and user ioctl dispatcher code in `smb_usr.c`.

## Behavior/Risks
This file is a privilege and namespace boundary for SMB client sessions. Zone checks prevent cross-zone ioctl access to device instances. Clone minor allocation is protected by `dev_lck`; stale soft-state or double-close mistakes would corrupt reference ownership. `smb_usr_dup_dev` and `smb_dev2share` must hold returned VC/share objects because device close can otherwise release them underneath callers. Module unload depends on both connection and password-keychain idleness.

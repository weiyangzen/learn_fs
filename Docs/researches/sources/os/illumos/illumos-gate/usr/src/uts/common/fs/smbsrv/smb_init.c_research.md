# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_init.c

## Role

Kernel module and pseudo-device entry point for the illumos SMB server driver.

## Major Responsibilities

- Defines global tunables for buffer size, flush behavior, symlink handling, signing debug, audit flags, advisory locks, thresholds, timeouts, and server thread priorities.
- Registers the SMB server pseudo-device driver module.
- Creates minor nodes for the control device and library-access device.
- Enforces privileged exclusive control opens for `smbd`.
- Creates and destroys `smb_server_t` instances through control-device open/close.
- Supports clone opens for library access.
- Validates ioctl headers, lengths, and CRCs.
- Enforces ioctl access policy by command class and opened device.
- Dispatches server configuration, lifecycle, share, event, enumeration, close, and spool-document ioctls.
- Copies ioctl results back for query-style operations.

## Key Functions

- `_init()` initializes global SMB server state and installs the module.
- `_info()` returns module info.
- `_fini()` refuses unload while servers exist, removes the module, and finalizes global state.
- `smb_drv_open()` routes opens by minor number.
- `smb_drv_open_ctl()` checks `secpolicy_smb()`, allocates a clone minor, and creates the SMB server instance.
- `smb_drv_open_lib()` allocates a clone minor for non-control library access.
- `smb_drv_close()` deletes the server when the control device closes and frees the clone minor.
- `smb_drv_ioctl()` validates/copies the ioctl payload, looks up the server, checks permissions, dispatches the ioctl command, and copies out results when needed.
- `smb_drv_attach()` creates `smbsrv` and `smbsrv1` minor nodes and initializes minor id space.
- `smb_drv_detach()` destroys minor id space and removes minor nodes.
- `smb_drv_getinfo()` maps device numbers to devinfo or instance values.

## Research Notes

The control minor is reserved for `smbd` and gates most mutating operations, while the library minor allows selected non-mutating or separately privileged operations. The ioctl path allocates at least the full union size to protect type-specific handlers from undersized user lengths.

# File Research: sources/os/linux/linux/fs/nfs/nfs40.h

## Purpose
Declares NFSv4.0-specific client, procedure, and state/trunking interfaces.

## Main Interfaces
- Client lifecycle: `nfs40_shutdown_client()`, `nfs40_init_client()`, `nfs40_handle_cb_pathdown()`.
- Minor-version operation table: `nfs_v4_0_minor_ops`.
- Trunking discovery: `nfs40_discover_server_trunking()`.

## Research Notes
This header is the v4.0-specific bridge among client setup, v4.0 procedure/state code, and generic v4 minor-version dispatch.

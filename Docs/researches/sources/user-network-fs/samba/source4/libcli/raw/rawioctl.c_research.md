<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/raw/rawioctl.c -->
# sources/user-network-fs/samba/source4/libcli/raw/rawioctl.c

Purpose: `rawioctl.c` implements raw SMB1 IOCTL operations through both the legacy `SMBioctl` command and NT transaction `NT_TRANSACT_IOCTL`.

Important APIs, types, and functions: Public entry points are `smb_raw_ioctl_send`, `smb_raw_ioctl_recv`, and `smb_raw_ioctl`. Internal helpers are `smb_raw_smbioctl_send`, `smb_raw_smbioctl_recv`, `smb_raw_ntioctl_send`, and `smb_raw_ntioctl_recv`. The code uses `union smb_ioctl`, `struct smb_nttrans`, `DATA_BLOB`, and raw request/blob helpers.

Control flow: `smb_raw_ioctl_send` switches on `parms->generic.level`. `RAW_IOCTL_IOCTL` builds an `SMBioctl` packet with file number and request code. `RAW_IOCTL_NTIOCTL` builds an NT transaction setup array containing function, file number, fsctl flag, and filter, passes caller input data, and sets `max_data` from the request. SMB2 IOCTL levels return `NULL`. Receive dispatch mirrors send: legacy IOCTL pulls the entire reply data area into a blob, while NT IOCTL receives an NT transaction and steals the returned data blob into the caller's memory context.

State and persistence behavior: Local state is request-scoped only. Server-side effects depend on the IOCTL/FSCTL function: some are pure queries, while others can mutate filesystem/device state. Returned blobs are caller-context allocations for NT IOCTL and direct request-pulled blobs for legacy IOCTL.

Dependencies and integration points: It depends on raw request setup, `smb_raw_nttrans_send/recv`, and blob memory helpers. Higher-level filesystem control operations and tests call it for SMB1; SMB2 IOCTLs must use SMB2-specific implementations matching the SMB2 branches in `interfaces.h`.

Risks: IOCTL payloads are opaque, so this layer cannot validate function-specific input/output structure. Legacy receive does not check WCT before pulling data, relying on generic receive state and buffer info. `smb_raw_ioctl_recv` returns `NT_STATUS_INVALID_LEVEL` for SMB2 levels, but a sync caller that got `NULL` from send still reaches recv. Memory ownership differs between legacy and NT paths.

Test signals: IOCTL/FSCTL torture tests should validate legacy and NT paths, zero-length blobs, large output bounded by `max_data`, server errors, invalid levels, and memory ownership of returned blobs. FSCTL-specific tests should run through higher-level wrappers as well as this raw interface.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/raw/rawioctl.c -->

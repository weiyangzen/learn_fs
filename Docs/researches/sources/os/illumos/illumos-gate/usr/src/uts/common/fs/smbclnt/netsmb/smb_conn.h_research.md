# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb_conn.h

## Purpose
Defines the primary SMB client connection, session, share, file-handle, request-list, and device-instance data structures and declares the connection, IOD, user ioctl, and file-handle APIs used across `netsmb`.

## Key Elements
Defines shared flags for object lifecycle (`SMBO_GONE`), VC behavior (`SMBV_UNICODE`, `SMBV_EXT_SEC`, `SMBV_SIGNING`, `SMBV_SMB2`, file-ID support, write-through quirks), share connection state, and file-handle validity. `smb_connobj` is the common embedded object for the hierarchy `SMBL_SM -> SMBL_VC -> SMBL_SHARE -> SMBL_FH`, with locks, use count, parent pointer, child SLIST, and callbacks.

`smb_sopt` stores negotiated SMB1 and SMB2+ server parameters, including dialect, signing/security mode, max mux, transfer sizes, capabilities, session flags, and server GUID. `smb_iods` stores SMB1 header defaults and signing sequence state. `smb_vc` combines connection identity, transport state, SMB1/2/3 negotiated state, signing/preauth/encryption key material, SMB2 message ID credit windows, IOD thread state, active request queue, session work buffers, and copied session identity.

`smb_share` represents a tree connection with TID/tree ID, share flags/capabilities, reconnect CVs, VC generation, and ioctl-provided share identity. `smb_fh` represents an SMB1 FID or SMB2 durable/volatile FID pair plus granted rights and VC generation. `smb_dev` represents one `/dev/nsmb` open instance and holds VC/share/FH references plus zone and ioctl serialization state.

## Dependencies
Includes illumos locking, queue, UIO, device, and crypto headers plus `smb_dev.h` user-visible ioctl structures. Declares APIs implemented in `smb_dev.c`, `smb_usr.c`, `smb_iod.c`, `smb_conn.c`, and protocol helpers.

## Behavior/Risks
This header is the ABI-like internal contract for the SMB client stack. Structure field changes affect ioctl paths, IOD reconnect logic, SMB2 credit accounting, SMB3 cryptography, mounted smbfs shares, and debug tooling. Several macros alias fields embedded in ioctl/session structures, so renames or layout changes can silently affect multiple modules. Key material is stored directly in `smb_vc`; teardown paths must continue clearing/freeing it carefully.

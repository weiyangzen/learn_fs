# File Research: sources/os/linux/linux-stable/fs/smb/client/smberr.h

## Summary
Defines classic SMB/CIFS error classes and error-code constants, with comments documenting their intended POSIX errno mappings. It is the legacy SMB error vocabulary used by SMB1-era mapping code and still retained in the client source tree.

## Main Responsibilities
- Define `struct smb_to_posix_error` entries pairing SMB error numbers with POSIX error codes.
- Define SMB error classes: `SUCCESS`, `ERRDOS`, `ERRSRV`, `ERRHRD`, and `ERRCMD`.
- Enumerate DOS-class errors such as invalid function, file not found, bad path, access denied, bad FID, sharing violation, lock conflict, disk full, invalid name, directory not empty, EA unsupported, quota exceeded, and symlink/internal passthrough cases.
- Enumerate server-class errors such as bad password, DFS referral, invalid TID/network name/device, print queue errors, invalid command, internal server error, bad permissions, paused server, timeout, no resources, too many UIDs, bad UID, notification enum, and account/password expiry cases.
- Preserve comments that are consumed or mirrored by mapping-table generation/maintenance expectations.

## Key Interfaces
This header is mostly constants rather than functions. The visible type is `struct smb_to_posix_error`, and the constants are named `ERR*`, `Err*`, and class names matching CIFS/SMB protocol terminology.

## Important Behavior
The comments after many defines document the Linux errno mapping intended by the client. Some values are not direct wire values but internal passthrough markers from NT status handling to POSIX errors. The header does not include guards in the displayed content, so it is intended for controlled inclusion in legacy error-mapping code rather than as a broad standalone API.

## Cross-File Interactions
Legacy CIFS error mapping code uses these definitions to translate SMB error-class/code pairs into Linux errnos. SMB2-specific error handling uses NT status mapping in separate code, but both ultimately feed the client’s POSIX-facing error returns.

## Risks
Changing values or mappings can alter user-visible errno behavior for legacy SMB/CIFS operations. Because the mappings are encoded in comments and constants, automated or manual table generation must keep comments, constants, and mapping tables synchronized.

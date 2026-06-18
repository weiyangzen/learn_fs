# File Research: sources/os/linux/linux/fs/smb/client/smberr.h

## Purpose

`smberr.h` defines legacy SMB/CIFS error classes and error-code constants, with comments indicating intended POSIX errno mappings. It supports mapping server SMB-class errors to Linux errors.

## Main Contents

- `struct smb_to_posix_error`, pairing an SMB error code with a POSIX code.
- SMB error classes: `SUCCESS`, `ERRDOS`, `ERRSRV`, `ERRHRD`, and `ERRCMD`.
- `ERRDOS` constants for filesystem and DOS-style failures such as invalid function, file not found, bad path, too many open files, access denied, bad file ID, no memory, invalid drive, cross-device rename, no more files, write protected, share conflict, lock conflict, unsupported operation, no such share, file exists, disk full, invalid name, directory not empty, quota, not-a-link, symlink, and too many links.
- `ERRSRV` constants for server/session/tree/authentication failures such as general server error, bad password, DFS referral needed, invalid TID, invalid network name, invalid device, print queue errors, bad command, paused server, timeout, too many UIDs, bad UID, notify enum dir, account expired, bad client, bad logon time, and password expired.

## Integration

- Consumed by SMB/CIFS error mapping code to translate protocol-specific status to Linux errno.
- Comments are structured so mapping tables can be generated or verified from the errno annotations.
- Complements SMB2/NTSTATUS mappings used elsewhere; this header is primarily for classic SMB error classes.

## Risk Notes

- These constants are protocol ABI and should not be renumbered.
- The POSIX mapping comments are semantically important for generated tables; editing comments can affect tooling if parsers rely on them.
- Some constants are internal passthrough values, not wire values, and should not be emitted as server SMB errors.

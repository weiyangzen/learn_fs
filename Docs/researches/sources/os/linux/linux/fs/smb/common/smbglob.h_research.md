# File Research: sources/os/linux/linux/fs/smb/common/smbglob.h

This common SMB header defines shared protocol-version values and RFC1001/1002 length helpers.

Key contents:
- `struct smb_version_values`, which describes negotiated protocol behavior: dialect string/id, lock commands, capabilities, maximum read/write/transaction sizes, credit limits, lock types, header sizes, response sizes, capability booleans, signing policy, and create-context sizes.
- `get_rfc1002_len()` reads the 24-bit length from a big-endian RFC1002 header.
- `inc_rfc1001_len()` increments the RFC1001 length field.
- String constants for SMB dialect names from SMB1 through SMB 3.1.1.
- Common I/O size constants, including `CIFS_DEFAULT_IOSIZE` and `MAX_CIFS_SMALL_BUFFER_SIZE`.

This is used by connection and response code to interpret stream framing and dialect-specific limits.

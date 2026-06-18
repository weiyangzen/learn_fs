# File Research: sources/os/linux/linux-stable/fs/smb/common/smbglob.h

Read status: complete.

## Purpose
Defines shared SMB version capability values and RFC1001/1002 length helpers.

## Main Contents
- `struct smb_version_values` for dialect-specific limits, capability bits, signing flags, header sizes, and create context sizes.
- `get_rfc1002_len()` and `inc_rfc1001_len()` helpers.
- SMB dialect version strings and default I/O/small-buffer size constants.

## Dependencies And Role
Used by SMB dialect tables and request/response construction code to abstract protocol-version differences.

## Risks
Version value fields are central to negotiated buffer sizing and dialect behavior. Incorrect values can under-allocate messages, advertise unsupported capabilities, or corrupt RFC1002 length framing.

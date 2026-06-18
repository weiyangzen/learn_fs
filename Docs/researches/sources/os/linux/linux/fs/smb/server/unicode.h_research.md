# File Research: sources/os/linux/linux/fs/smb/server/unicode.h

Declares ksmbd Unicode/string conversion APIs.

Key contents:
- Includes byteorder, NLS, Unicode, and UCS-2 utility headers.
- Exports UTF-16 conversion, UTF-16 string duplication to local codepage, mapped UTF-16 conversion, and share-name extraction helpers under `__KERNEL__`.

Role in subsystem:
- Header for SMB path/share-name encoding and decoding helpers used by protocol and VFS paths.

# File Research: sources/os/linux/linux/fs/smb/client/smb1pdu.h

This header defines SMB1/CIFS command constants, flags, packed wire structures, information levels, Unix Extensions layouts, and POSIX-extension helper formats.

Major definition groups:
- Protocol and command IDs for classic SMB commands, Transaction2 subcommands, named-pipe transactions, and NT transactions.
- SMB header limits, authentication/key sizes, open/access flags, SMB flags/flags2, file attributes, share access, create disposition/options, impersonation/security flags, and default identifiers.
- Negotiation response layout, security mode bits, and capability bits including Unicode, NT SMBs, DFS, large read/write, Unix Extensions, compression, and extended security.
- Session setup request/response union covering extended-security NTLM, no-security-extension NTLM, and old pre-NTLM/LANMAN formats.
- Tree connect, echo, logoff, close, flush, find-close, open/create, read, write, lock, rename/copy/delete/create-directory/query/setattr packet layouts.
- NT transaction structures for IOCTL/FSCTL, compression IOCTL, security descriptor get/set, change notify, and quota data.
- Transaction2 generic request/response wrappers plus query/set path/file info, find-first/find-next, filesystem info, set filesystem info, and DFS referral structures.
- Data layouts for `FILE_ALL_INFO`, `FILE_STANDARD_INFO`, `FILE_UNIX_BASIC_INFO`, Unix symlink targets, DOS date/time, allocation/EOF/compression info, POSIX ACLs, POSIX open/unlink, internal file ids, file mode, and reparse attribute/tag.
- Directory enumeration records such as `FILE_UNIX_INFO` and `FIND_FILE_STANDARD_INFO`.
- EA list/blob helpers and optional POSIX/xattr/chattr structures under `CONFIG_CIFS_POSIX`.

Important constants:
- `ATTR_REPARSE_POINT` and `OPEN_REPARSE_POINT` connect this header to reparse handling.
- `SMB_FILE_REPARSEPOINT_INFO`, `struct file_attrib_tag`, and NT transaction IOCTL layouts support reparse-point query/create paths.
- CIFS Unix capability flags drive negotiation in `smb1ops.c`.

Implementation note:
- Most structs are `__packed` wire-format declarations. Correct endian annotations and alignment/padding are critical because request builders and response parsers cast network buffers directly to these types.

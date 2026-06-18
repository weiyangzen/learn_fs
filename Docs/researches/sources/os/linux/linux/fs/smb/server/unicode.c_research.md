# File Research: sources/os/linux/linux/fs/smb/server/unicode.c

Implements SMB string conversion between local codepages/UTF-8 and SMB UTF-16LE wire strings.

Key behaviors:
- Converts single UTF-16 code units or multiword sequences to local codepage bytes, including mapped reserved SMB characters.
- Computes converted UTF-16LE string byte length before allocation.
- Converts UTF-16LE input to local charset with destination bounds and null termination.
- Converts local strings to UTF-16LE, with a fast UTF-8 path via `utf8s_to_utf16s`.
- Falls back to `?` on invalid/unrepresentable characters.
- Supports surrogate pairs and IVS-style multiword UTF-16/UTF-8 handling for UTF-8 codepages.
- Maps POSIX-visible reserved characters such as `:`, `*`, `?`, `<`, `>`, and `|` to SMB private Unicode code points when requested.
- Provides `smb_strndup_from_utf16()` for allocating converted inbound strings.

Dependencies:
- Uses Linux NLS tables, Unicode helpers, unaligned endian access, and constants from `nls_ucs2_utils.h`.

Role in subsystem:
- Essential path/name conversion layer between SMB wire format and Linux VFS strings.

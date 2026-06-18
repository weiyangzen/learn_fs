# File Research: sources/virtualization/libguestfs/lib/journal.c

Purpose: Implements `journal_get` library-side to avoid protocol limits for large systemd journal fields.

Key behavior:
- Calls `guestfs_internal_journal_get` to download a private binary stream to a temp file.
- Reads the whole temp file locally, then parses repeated records of big-endian 64-bit length followed by `field=data` bytes.
- Builds a `guestfs_xattr_list`, storing the field name as `attrname` and binary value as `attrval`.
- Validates truncation, oversized length, and missing `=` separator with explicit errors.

Dependencies and state:
- Depends on temp path creation, full-read, endian conversion, generated internal journal action, and xattr list allocation/free helpers.
- Stateless beyond temp files.

Risks:
- Reads the whole exported journal record stream into memory.
- Protocol is private and explicitly may change; producer and parser must remain in sync.

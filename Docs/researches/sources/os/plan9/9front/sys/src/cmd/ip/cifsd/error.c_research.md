# File Research: sources/os/plan9/9front/sys/src/cmd/ip/cifsd/error.c

Maps Plan 9 and NT-style errors into SMB/DOS error encodings.

Key points:
- Defines SMB error classes and DOS/server/hardware command error codes.
- `doserror` maps NT status values to packed DOS/class error values for clients that did not negotiate NT status.
- `smbmkerror` reads the current Plan 9 error string and matches substrings to NT status values.
- Includes mappings for permission denied, directory not empty, no such file/name/path, bad syntax, collision, directory type errors, and several kenfs-specific wstat/create errors.
- Falls back to `STATUS_INVALID_SMB` for unknown errors.
- Debug mode logs error-string-to-status mapping.

Dependencies and interactions:
- Used by SMB request response paths and file/path operation code.

Research relevance:
- Critical compatibility layer between Plan 9 error strings and CIFS/SMB client-visible status codes.

# sources/test-tools/strace/src/statmount.c

Purpose: decodes the modern `statmount` syscall request and variable-length mount-stat response.

Important APIs/types/functions: `print_quoted_cstring_sequence`, `print_mnt_id_req`, `print_statmount`, `SYS_FUNC(statmount)`, `PRINT_FIELD_CSTRING_OFFSET`, `PRINT_FIELD_CSTRING_SEQUENCE`, and xlat tables for statmount flags/masks, superblock flags, and mount propagation.

Control flow: entry prints a versioned `mnt_id_req`: first reads `size`, then fetches available fields, including namespace fd, mount id, parameter mask, optional namespace id, and nonzero unknown tail bytes. Exit fetches `struct statmount` up to caller buffer size, optionally fetches trailing string storage, and prints fields only when their mask bits are set. String fields are offsets into the trailing buffer; string sequences iterate null-terminated entries with truncation checks.

State and persistence behavior: stateless local copies. It reads at most one page of unknown request tail and caps string-buffer reads to `PATH_MAX * 3`.

Dependencies and integration points: depends on Linux mount UAPI, `fsmagic`, `mount_attr_attr`, sequence truncation helpers, and syscall table mapping for new mount APIs.

Risks: `statmount` is versioned and still evolving; mask-gated fields, offset strings, and trailing arrays are easy to misalign. Invalid offsets are printed numerically. New mask bits require printer updates and xlat additions.

Test signals: old/new `mnt_id_req` sizes, request tail bytes, all mask groups, invalid string offsets, truncated string sequences, option/security/uidmap/gidmap arrays, supported mask, flags, and short buffers.

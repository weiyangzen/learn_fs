<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/umounttab.h -->
# sources/security-integrity/audit-userspace/auparse/umounttab.h

Purpose: macro table for interpreting `umount` flag bits from Linux `include/linux/fs.h`.

Important APIs and types: `_S` maps `0x1` to `MNT_FORCE`, `0x2` to `MNT_DETACH`, `0x4` to `MNT_EXPIRE`, `0x8` to `UMOUNT_NOFOLLOW`, and `0x80000000` to `UMOUNT_UNUSED`.

Control flow and state: none; consumers define `_S` to build conversion tables.

Dependencies and integration: used by auparse generated flag interpretation logic for unmount-related audit fields. It is source-synchronized with kernel constants rather than computed from system headers.

Risks and test signals: stale constants or missing new flags would produce incomplete interpretation. Signal is indirect through generated lookup/flag tests and audit event interpretation output.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/umounttab.h -->

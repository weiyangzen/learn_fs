<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/xattr-atflagtab.h -->
# sources/security-integrity/audit-userspace/auparse/xattr-atflagtab.h

Purpose: macro table for interpreting `*xattrat`/`AT_*` flag bits related to extended attribute operations.

Important APIs and types: `_S` rows map `AT_SYMLINK_NOFOLLOW`, `AT_NO_AUTOMOUNT`, `AT_EMPTY_PATH`, and `AT_RECURSIVE`. A comment notes zero/`LOOKUP_FOLLOW` is handled in code rather than as a table row.

Control flow and state: no executable logic; generated-table consumers provide `_S`.

Dependencies and integration: tied to Linux `include/uapi/linux/fcntl.h` and `fs/xattr.c` semantics and consumed by auparse flag interpretation.

Risks and test signals: missing kernel flag updates can make audit interpretation less useful. The zero-flag special case must remain aligned with code that handles default follow behavior. Tests are generated lookup/interpretation checks and any fixture output that includes xattr flags.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/xattr-atflagtab.h -->

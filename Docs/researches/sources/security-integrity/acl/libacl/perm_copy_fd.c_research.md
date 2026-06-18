<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/libacl/perm_copy_fd.c -->
# sources/security-integrity/acl/libacl/perm_copy_fd.c

Purpose: fd-to-fd permission preservation helper used by cp-like callers. The shared ACL library stores public opaque handles as internal objects tagged with libobj magic values, orders entries in the canonical POSIX ACL sequence, and translates between text, in-memory rings, and Linux `system.posix_acl_*` extended attributes. The file is 203 lines.

Important APIs and functions: Key symbols include `acl_free`, `acl_entries`, `acl_from_mode`, `set_acl_fd`, `perm_copy_fd`, `ERROR_CONTEXT_MACROS`.

Control flow: Stats the source fd, reads its ACL when available, applies it to the destination fd, falls back through mask-adjusted `fchmod` for base ACLs or unsupported ACL filesystems, and reports errors through `error_context`.

State and persistence: Mutated state is usually an in-memory `acl_obj`, `acl_entry_obj`, embedded `acl_permset_obj`, or temporary xattr/text buffer. Path/fd setters and delete helpers persist ACL state to Linux extended attributes or mode bits; pure manipulation helpers only affect caller-owned handles until later applied.

Dependencies and integration points: Depends on private `libacl.h` object macros, `libobj` validation/allocation, POSIX ACL constants, libc allocation/errno, `sys/xattr.h` for filesystem persistence where relevant, `byteorder.h`/`acl_ea.h` for xattr layout, `misc.h` for parsing/lookup/text support, and libattr error-context APIs in permission-copy helpers.

Risks: Handle validation, canonical ordering, iterator state, and errno conventions are cross-cutting invariants. Xattr serializers must preserve little-endian kernel layout, fallback chmod paths must not widen effective permissions, and text/name parsing must treat malformed input as `EINVAL` without leaking partially built ACLs.

Test signals: Unit or integration coverage should exercise valid and malformed ACL handles, canonical ordering, text round trips, xattr get/set/delete on files and directories, unsupported-filesystem fallbacks, mask recalculation/equivalence, named user/group qualifiers, iterator deletion, and `getfacl`/`setfacl` command tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/libacl/perm_copy_fd.c -->

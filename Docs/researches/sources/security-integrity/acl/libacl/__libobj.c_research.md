<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/libacl/__libobj.c -->
# sources/security-integrity/acl/libacl/__libobj.c

Purpose: Implementation of the private tagged-object allocator and validator used by all opaque ACL handles. The shared ACL library stores public opaque handles as internal objects tagged with libobj magic values, orders entries in the canonical POSIX ACL sequence, and translates between text, in-memory rings, and Linux `system.posix_acl_*` extended attributes. The file is 93 lines.

Important APIs and functions: Key symbols include `__acl_new_var_obj_p`, `__acl_new_obj_p_here`, `__acl_free_obj_p`, `__acl_check_obj_p`.

Control flow: Allocates variable-size objects with magic prefixes, supports in-place object initialization, validates external-to-internal conversions, and frees only heap-owned objects.

State and persistence: Mutated state is usually an in-memory `acl_obj`, `acl_entry_obj`, embedded `acl_permset_obj`, or temporary xattr/text buffer. Path/fd setters and delete helpers persist ACL state to Linux extended attributes or mode bits; pure manipulation helpers only affect caller-owned handles until later applied.

Dependencies and integration points: Depends on private `libacl.h` object macros, `libobj` validation/allocation, POSIX ACL constants, libc allocation/errno, `sys/xattr.h` for filesystem persistence where relevant, `byteorder.h`/`acl_ea.h` for xattr layout, `misc.h` for parsing/lookup/text support, and libattr error-context APIs in permission-copy helpers.

Risks: Handle validation, canonical ordering, iterator state, and errno conventions are cross-cutting invariants. Xattr serializers must preserve little-endian kernel layout, fallback chmod paths must not widen effective permissions, and text/name parsing must treat malformed input as `EINVAL` without leaking partially built ACLs.

Test signals: Unit or integration coverage should exercise valid and malformed ACL handles, canonical ordering, text round trips, xattr get/set/delete on files and directories, unsupported-filesystem fallbacks, mask recalculation/equivalence, named user/group qualifiers, iterator deletion, and `getfacl`/`setfacl` command tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/libacl/__libobj.c -->

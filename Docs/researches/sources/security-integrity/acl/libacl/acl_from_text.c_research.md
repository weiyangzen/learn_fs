<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/libacl/acl_from_text.c -->
# sources/security-integrity/acl/libacl/acl_from_text.c

Purpose: Public text parser for ACL entries. The shared ACL library stores public opaque handles as internal objects tagged with libobj magic values, orders entries in the canonical POSIX ACL sequence, and translates between text, in-memory rings, and Linux `system.posix_acl_*` extended attributes. The file is 259 lines.

Important APIs and functions: Key symbols include `parse_acl_entry`, `acl_from_text`, `skip_tag_name`, `get_token`, `SKIP_WS`.

Control flow: Skips whitespace/comments, parses user/group/mask/other tags and optional qualifiers, resolves names or ids, decodes rwx permission text, creates entries, and copies parsed state into the ACL.

State and persistence: Mutated state is usually an in-memory `acl_obj`, `acl_entry_obj`, embedded `acl_permset_obj`, or temporary xattr/text buffer. Path/fd setters and delete helpers persist ACL state to Linux extended attributes or mode bits; pure manipulation helpers only affect caller-owned handles until later applied.

Dependencies and integration points: Depends on private `libacl.h` object macros, `libobj` validation/allocation, POSIX ACL constants, libc allocation/errno, `sys/xattr.h` for filesystem persistence where relevant, `byteorder.h`/`acl_ea.h` for xattr layout, `misc.h` for parsing/lookup/text support, and libattr error-context APIs in permission-copy helpers.

Risks: Handle validation, canonical ordering, iterator state, and errno conventions are cross-cutting invariants. Xattr serializers must preserve little-endian kernel layout, fallback chmod paths must not widen effective permissions, and text/name parsing must treat malformed input as `EINVAL` without leaking partially built ACLs.

Test signals: Unit or integration coverage should exercise valid and malformed ACL handles, canonical ordering, text round trips, xattr get/set/delete on files and directories, unsupported-filesystem fallbacks, mask recalculation/equivalence, named user/group qualifiers, iterator deletion, and `getfacl`/`setfacl` command tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/libacl/acl_from_text.c -->

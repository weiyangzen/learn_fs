# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/uuid_clear.3.in

Purpose: manpage template for `uuid_clear()`, documenting how to reset a UUID variable to the NULL UUID.

Important APIs, types, and functions: documents `void uuid_clear(uuid_t uu)` from `<uuid/uuid.h>`.

Control flow: documentation only; `.TH` uses e2fsprogs version/date substitutions and `.SH` sections describe synopsis, behavior, author, availability, and see-also links.

State and persistence: after installation, persists as API documentation. It describes a function that mutates the caller's UUID buffer to all-zero/null value.

Dependencies and integration points: must match public declaration in `uuid.h.in` and implementation in the libuuid source outside this work item. Cross-references other UUID manpages.

Risks: minimal, but stale docs could mislead about null UUID semantics if implementation changes.

Test signals: documentation generation via substitution and `man` formatting checks; `tst_uuid.c` checks `uuid_clear()` followed by `uuid_is_null()`.

# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/uuid_copy.3.in

Purpose: manpage template for `uuid_copy()`, documenting copying one UUID value to another.

Important APIs, types, and functions: documents `void uuid_copy(uuid_t dst, uuid_t src)` as declared in the public header.

Control flow: documentation only. The page states that `src` is copied to `dst` and that the copied UUID is returned in the destination location.

State and persistence: installed manpage. The described function mutates the destination UUID buffer but has no persistent library state.

Dependencies and integration points: tied to `uuid.h.in` and the copy implementation outside this work item. Used in `tst_uuid.c` before `uuid_compare()`.

Risks: array parameter constness in the manpage is less precise than the header (`const uuid_t src` in `uuid.h.in`). Documentation should avoid implying a returned value because the function returns `void`; the current wording means "stored", not a C return.

Test signals: `tst_uuid.c` copy-and-compare path. Manpage substitution should fill date and version placeholders.

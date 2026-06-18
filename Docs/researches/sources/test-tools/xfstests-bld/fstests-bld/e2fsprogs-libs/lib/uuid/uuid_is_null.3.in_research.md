# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/uuid_is_null.3.in

Purpose: manpage template for `uuid_is_null()`, documenting comparison against the NULL UUID.

Important APIs, types, and functions: documents `int uuid_is_null(uuid_t uu)`, with return value 1 for null UUID and 0 otherwise.

Control flow: documentation only.

State and persistence: installed API documentation. The function described reads the UUID buffer and does not mutate persistent state.

Dependencies and integration points: paired with `uuid_clear.3.in` and public declaration in `uuid.h.in`. `tst_uuid.c` tests it immediately after `uuid_clear()`.

Risks: no major implementation risks in the template. Header constness is more precise than the manpage if the public prototype uses `const uuid_t`.

Test signals: clear-then-is-null and nonzero UUID checks. Manpage substitution and formatting should be part of doc build validation.

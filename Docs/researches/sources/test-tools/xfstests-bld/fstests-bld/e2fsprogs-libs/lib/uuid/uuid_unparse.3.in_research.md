# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/uuid_unparse.3.in

Purpose: manpage template for converting binary UUIDs to text with `uuid_unparse()`, `uuid_unparse_upper()`, and `uuid_unparse_lower()`.

Important APIs, types, and functions: documents the three unparse functions and the required output buffer for a 36-byte string plus trailing NUL.

Control flow: documentation only. It states that `uuid_unparse()` default case may be system-dependent, while upper/lower variants provide deterministic case.

State and persistence: installed API documentation. The described functions write caller-provided output buffers.

Dependencies and integration points: must match `unparse.c`, `uuid.h.in`, and `uuid_parse.3.in`. Cross-references the broader UUID API.

Risks: the page has a typo "tailing" for trailing. The buffer-size requirement is critical because implementation uses `sprintf()`. Any build-time default case macro change should still be compatible with this wording.

Test signals: fixed byte-array to lower/upper string tests, parse-unparse round trip, and manpage substitution checks.

# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/unparse.c

Purpose: `unparse.c` converts a binary `uuid_t` into canonical hyphenated UUID text in lower-case, upper-case, or build-configured default case.

Important APIs, types, and functions: public functions are `uuid_unparse()`, `uuid_unparse_lower()`, and `uuid_unparse_upper()`. The internal `uuid_unparse_x()` unpacks the UUID and formats using either `fmt_lower` or `fmt_upper`. It depends on `uuid_unpack()` and `struct uuid`.

Control flow: `uuid_unparse_x()` calls `uuid_unpack()` and then writes to the caller's `out` buffer using `sprintf()` with the format `%08x-%04x-%04x-%02x%02x-%02x...`. The `clock_seq` field is split into two bytes for the fourth UUID group, and the six node bytes form the final group. The default `uuid_unparse()` chooses upper case only when `UUID_UNPARSE_DEFAULT_UPPER` is defined; otherwise it uses lower case.

State and persistence: stateless; it only writes formatted text to the caller's buffer. The caller must provide enough space for 36 characters plus NUL.

Dependencies and integration points: declared in `uuid.h.in`, documented in `uuid_unparse.3.in`, and used by `tst_uuid.c`. Its output is accepted by `uuid_parse()` and is usually the user-facing representation of generated UUIDs.

Risks: uses `sprintf()` rather than bounded formatting, so the API contract requires a sufficiently large output buffer. Any change to format width, hyphen placement, or case default can affect ABI/user expectations. It assumes `uuid_unpack()` returns fields normalized to integer values.

Test signals: `tst_uuid.c` prints generated UUID strings and parses a generated time UUID back for comparison. Additional stable tests should validate known byte arrays against exact lower and upper strings.

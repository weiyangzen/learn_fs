# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/unpack.c

Purpose: `unpack.c` implements the private inverse of `uuid_pack()`: it converts the public 16-byte `uuid_t` representation into a structured `struct uuid`.

Important APIs, types, and functions: the file exports `void uuid_unpack(const uuid_t in, struct uuid *uu)`. It uses `uint8_t`, `uint32_t`, `memcpy()`, and `struct uuid` from `uuidP.h`.

Control flow: the function walks the input byte array with a pointer. It accumulates bytes into integer fields using left shifts and ORs: bytes 0-3 become `time_low`, 4-5 `time_mid`, 6-7 `time_hi_and_version`, and 8-9 `clock_seq`. It copies bytes 10-15 into `node`.

State and persistence: no state beyond the caller-provided output struct. It performs no allocation or I/O and has no persistence.

Dependencies and integration points: `uuid_unparse()` calls `uuid_unpack()` before formatting. `uuid_time()`, `uuid_type()`, and `uuid_variant()` call it to inspect UUID internals. The byte order must remain synchronized with `uuid_pack()`.

Risks: no null or size checks are performed; callers must provide a valid 16-byte input and writable struct. The manual decode is endian-stable. Any field order mistake would corrupt formatted UUIDs and timestamp/variant extraction.

Test signals: `tst_uuid.c` exercises this through unparse, compare after parse/unparse, type/variant checks, and time extraction. A good regression test is a known UUID byte array with expected textual form and timestamp fields.

# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/pack.c

Purpose: `pack.c` implements the private `uuid_pack()` conversion from the library's structured `struct uuid` view into the public 16-byte `uuid_t` wire/storage representation. It is part of the e2fsprogs/libuuid compatibility implementation and enforces the DCE UUID field byte order independent of host endian layout.

Important APIs, types, and functions: the only exported function in this file is `void uuid_pack(const struct uuid *uu, uuid_t ptr)`. It depends on `struct uuid` and `uuid_t` from `uuidP.h` and uses `uint32_t` temporaries for field shifts. The fields packed are `time_low`, `time_mid`, `time_hi_and_version`, `clock_seq`, and the six-byte `node`.

Control flow: `uuid_pack()` casts the output array to `unsigned char *`, then writes integer fields byte-by-byte in big-endian UUID text/network order: `time_low` into bytes 0-3, `time_mid` into 4-5, `time_hi_and_version` into 6-7, and `clock_seq` into 8-9. It copies `node` directly into bytes 10-15 with `memcpy()`.

State and persistence: the function is stateless and performs no allocation or I/O. Its only side effect is writing exactly 16 bytes to the caller-provided `uuid_t`.

Dependencies and integration points: `uuid_parse()` builds a `struct uuid` from text and calls `uuid_pack()` to produce the public binary form. UUID generators elsewhere in libuuid can also use this helper. `uuid_unpack()` in `unpack.c` is the inverse operation, and `uuid_unparse()` depends on that inverse.

Risks: callers must pass a valid output buffer of at least 16 bytes and a fully initialized `struct uuid`. The function does no null checks and silently truncates higher bits if callers put values larger than the declared field widths into the struct. The manual byte order is correct for UUID layout but should not be replaced with raw struct copies because that would be host-endian and padding-sensitive.

Test signals: `tst_uuid.c` exercises this path indirectly through `uuid_parse()`, `uuid_unparse()`, and `uuid_compare()`. Round-trip string/binary tests are the strongest signal for regressions in field order.

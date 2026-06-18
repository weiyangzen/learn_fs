# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/uuid_time.c

Purpose: `uuid_time.c` inspects UUID internals to extract timestamp, type, and variant metadata. It explicitly crosses the abstraction boundary by interpreting fields inside a UUID.

Important APIs, types, and functions: public functions are `time_t uuid_time(const uuid_t uu, struct timeval *ret_tv)`, `int uuid_type(const uuid_t uu)`, and `int uuid_variant(const uuid_t uu)`. Under `DEBUG`, it also provides a CLI-style `main()` and `variant_string()` for inspecting one UUID string.

Control flow: `uuid_time()` unpacks the UUID, combines the low 32 bits with the high timestamp bits from `time_mid` and low 12 bits of `time_hi_and_version`, subtracts the UUID-to-Unix epoch offset, and converts 100ns ticks into seconds and microseconds. `uuid_type()` unpacks and returns the high 4 version bits from `time_hi_and_version`. `uuid_variant()` unpacks and classifies the high bits of `clock_seq` into NCS, DCE, Microsoft, or other. The debug `main()` parses an input UUID, prints variant/type, warns for non-DCE or non-time UUIDs, and prints decoded time.

State and persistence: no persistent state. It writes to `ret_tv` when non-null and returns scalar metadata. Debug mode prints to stdout/stderr.

Dependencies and integration points: depends on `uuidP.h`, `uuid_unpack()`, public constants from `uuid.h.in`, and system time headers. `tst_uuid.c` validates type, variant, and time extraction for generated UUIDs. Manpage `uuid_time.3.in` documents the timestamp API.

Risks: `uuid_time()` does not validate that the UUID is DCE version 1 before decoding; callers can pass random UUIDs and get meaningless time values. Arithmetic assumes `uint64_t` availability through private integer type setup. Formatting in debug/test paths uses `%ld` for timeval fields, which may be platform-sensitive. The epoch offset is hard-coded rather than using the named `TIME_OFFSET_*` macros, so duplicated constants must remain synchronized.

Test signals: `tst_uuid.c` checks version 1 for `uuid_generate_time()`, version 4 for random UUIDs, and DCE variant for generated UUIDs. Add fixed vector tests for UUID timestamp decoding to guard the 100ns and epoch arithmetic.

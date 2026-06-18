# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/uuid_time.3.in

Purpose: manpage template for `uuid_time()`, documenting extraction of a Unix timestamp from time-based UUIDs.

Important APIs, types, and functions: documents `time_t uuid_time(uuid_t uu, struct timeval *ret_tv)`. It says seconds are returned and seconds plus microseconds are stored in `ret_tv`.

Control flow: documentation only. It warns that only certain UUID types encode creation time and that reliable extraction is expected for UUIDs from `uuid_generate_time()`.

State and persistence: installed manpage. The described function reads a UUID and optionally writes a caller-provided `struct timeval`.

Dependencies and integration points: must match `uuid_time.c`, `uuid_generate.3.in`, and the public prototype in `uuid.h.in`. `tst_uuid.c` generates a time UUID and calls `uuid_time()`.

Risks: docs should emphasize that non-time UUIDs can produce meaningless timestamps. Header constness is more precise than the synopsis. Time conversion depends on UUID epoch constants in `uuidP.h`.

Test signals: known version-1 UUID timestamp tests, generated time UUID type checks, and doc substitution/formatting checks.

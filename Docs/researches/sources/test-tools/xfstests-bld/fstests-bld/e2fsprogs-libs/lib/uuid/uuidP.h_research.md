# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/uuidP.h

Purpose: `uuidP.h` is the private libuuid header for internal structure layout and pack/unpack helpers.

Important APIs, types, and functions: it defines `TIME_OFFSET_HIGH`, `TIME_OFFSET_LOW`, and `struct uuid` with fields `time_low`, `time_mid`, `time_hi_and_version`, `clock_seq`, and `node[6]`. It declares `uuid_pack()` and `uuid_unpack()`.

Control flow: preprocessor flow chooses `<inttypes.h>` when available or `<uuid/uuid_types.h>` otherwise, then includes `<sys/types.h>` and the public `<uuid/uuid.h>`.

State and persistence: no runtime state. The struct definition is private but central to internal interpretation of binary UUIDs.

Dependencies and integration points: used by `pack.c`, `unpack.c`, `parse.c`, `unparse.c`, `uuid_time.c`, and likely UUID generation files outside this work item. The time offset constants correspond to the UUID epoch offset from 15-Oct-1582 to Unix epoch.

Risks: changing `struct uuid` field widths or semantics would break every internal conversion. Because the public representation is a byte array, this struct must remain an internal logical view, not a serialized layout.

Test signals: compile all libuuid implementation files and run `tst_uuid.c`. Known UUID timestamp and string round-trip tests validate this header's field model.

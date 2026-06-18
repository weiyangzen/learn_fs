# Research: sources/user-network-fs/samba/source3/lib/netapi/tests/netdisplay.c

Purpose: integration tests for `NetQueryDisplayInformation` display enumeration. It checks user, machine, and group display levels.

Important APIs/functions: `test_netquerydisplayinformation` loops over `NetQueryDisplayInformation` for a level, casts returned buffers to `NET_DISPLAY_USER`, `NET_DISPLAY_MACHINE`, or `NET_DISPLAY_GROUP`, optionally searches for a supplied name, and frees each buffer. `netapitest_display` runs levels 1, 2, and 3.

Control flow: enumeration starts at index 0, requests up to 1000 entries and unlimited preferred length, increments `idx` by `entries_read`, and repeats while status is `ERROR_MORE_DATA`. It treats both success and more-data as readable buffers.

State and persistence: read-only against the target account database. Process-local state is limited to temporary buffers and counters. Buffers are released with `NetApiBufferFree`.

Dependencies/integration: depends on public display structs in `netapi.h` and shared status helpers in `common.h`. `netapitest.c` runs this after user/group modules, but this file does not require a specific test account unless `name` is supplied.

Risks: advancing by `entries_read` assumes the API's index contract matches this simple pattern; some display APIs expose `next_index` fields that may be more precise. If `entries_read` is zero with `ERROR_MORE_DATA`, the loop could spin. Name matching is case-insensitive through `strcasecmp`, which matches Windows-ish expectations but is locale-sensitive.

Test signals: run levels 1-3 against a populated domain, verify multi-page enumeration, validate optional name search, and include a guard test for zero-entry more-data behavior if the server can produce it.

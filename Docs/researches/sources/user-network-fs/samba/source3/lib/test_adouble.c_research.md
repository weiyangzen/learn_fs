## sources/user-network-fs/samba/source3/lib/test_adouble.c

Purpose: cmocka regression tests for AppleDouble parsing safety in `adouble.c`, included directly into the test translation unit to access implementation internals.

Important fixtures are byte arrays `ad_basic`, `ad_finderinfo1/2/3`, `ad_name`, and `ad_date1/2`, plus helper `parse_adouble`. Test cases exercise valid FinderInfo/resource fork layouts, empty entries, and dangerous offset/length combinations for FinderInfo, name, and date entries.

Control flow: group setup creates a talloc stackframe and teardown frees it. `parse_adouble` allocates an `adouble`, copies the fixture into `ad->ad_data`, and calls `ad_unpack(ad, 2, filesize)`. Individual tests assert whether parsing succeeds and whether `ad_get_entry` returns non-null/null for expected entries. `main` optionally accepts a cmocka filter, emits subunit output, and runs the test group.

State and persistence: no persistence. State is per-test talloc memory and static fixture data. Dependencies are `adouble.c`, cmocka, talloc, and AppleDouble constants such as `ADEID_FINDERI` and `ADEID_FILEDATESI`.

Risks: direct inclusion of `adouble.c` can hide linkage issues and couples the test to implementation details. The test names contain `abouble` typos but are harmless. The key signal is bounds-check coverage for offset+length validation and empty entry handling, guarding against out-of-bounds reads from malformed AppleDouble metadata.

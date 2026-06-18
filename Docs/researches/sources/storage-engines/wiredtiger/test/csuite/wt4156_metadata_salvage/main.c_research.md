# sources/storage-engines/wiredtiger/test/csuite/wt4156_metadata_salvage/main.c

## Purpose
WT-4156 tests metadata and turtle-file salvage after deliberate corruption. It creates many metadata entries, corrupts selected bytes in `WiredTiger.wt` and `WiredTiger.turtle`, verifies open behavior, opens with `salvage=true`, and checks salvaged metadata and table data.

## Important APIs, Types, and Functions
- Uses `TABLE_INFO` to describe expected objects and key/value formats.
- `byte_str` searches binary buffers for text despite embedded zeros.
- `create_data` creates tables/files with large `app_metadata` to spread metadata entries across pages.
- `corrupt_file` reads metadata/turtle files, replaces occurrences of a target URI string with `X`, and writes bytes back.
- `verify_metadata` walks the `metadata:` cursor and opens salvaged objects to verify data.
- `open_with_corruption`, `open_with_salvage`, and `open_normal` cover expected corruption, salvage, and post-salvage reopen paths.
- `copy_database` preserves database, metadata, and turtle snapshots for debugging.

## Control Flow
The test skips ASAN bypass and TSAN builds. It opens a clean home, creates several file and table objects plus one corrupt target, inserts one record into each, closes, and copies the database to `SAVE`. It corrupts `WiredTiger.wt`, saves that corrupt file, and runs corruption/salvage/normal verification. It then corrupts `WiredTiger.turtle`, saves the corrupt turtle, and repeats verification. Finally it removes the saved copy and cleans up.

## State and Persistence Behavior
Persistent state is central: many data files, `WiredTiger.wt`, `WiredTiger.turtle`, saved copies, `.CORRUPT` files, and `WiredTiger.wt.slvg` expected after salvage. The global `home`, `wt_session`, `test_abort`, and `test_out_of_sync` coordinate helper behavior.

## Dependencies and Integration Points
The test uses direct filesystem I/O, WiredTiger metadata cursor semantics, salvage open configuration, debug corruption mode, and `testutil_copy_ext`. It assumes metadata page size behavior through `APP_MD_SIZE`/`APP_BUF_SIZE`.

## Risks and Test Signals
Failure signals include missing corruption target string, unexpected open error, missing salvage file, salvaged corrupt object appearing when it should not, missing expected metadata entries, or data mismatch. Directly editing WiredTiger metadata makes the test sensitive to metadata encoding and file naming changes.

# sources/storage-engines/wiredtiger/test/csuite/wt3120_filesys/main.c

## Purpose
WT-3120 validates that a simple filesystem extension can be loaded early, used for a small table workload, closed, and followed by a normal reopen with data intact.

## Important APIs, Types, and Functions
- Uses `TEST_OPTS`, `WT_SESSION`, `WT_CURSOR`, `wiredtiger_open`, and standard test utility helpers.
- Loads `WT_FAIL_FS_LIB` through `extensions=(...=(early_load=true))`.
- Uses string-key/string-value table operations through the URI in `opts->uri`.

## Control Flow
The test parses options, recreates the home, builds an extension path from the build directory, and opens WiredTiger with fail filesystem extension early-loaded. It creates a string table, inserts keys `a` and `b`, closes the cursor/session/connection to force data to disk, reopens without the extension, and verifies the two records in order.

## State and Persistence Behavior
The table is persisted across close and reopen. Statistics logging is enabled in both open configurations. No failure injection is enabled; the extension load itself is the focus.

## Dependencies and Integration Points
The test depends on the fail filesystem shared library, `testutil_build_dir`, and extension loading. It integrates with the csuite binary options for home, URI, and build directory.

## Risks and Test Signals
Failure signals include extension load failure, close/reopen failure, missing records, wrong key/value ordering, or unexpected extra records. It is a narrow smoke test: it does not exercise fail_fs failure controls.

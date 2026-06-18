<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/live_restore/live_restore.h -->
# sources/storage-engines/wiredtiger/src/live_restore/live_restore.h

## Purpose
Declares the live-restore public-internal interface used by the rest of WiredTiger. It exposes persisted file-handle metadata and prototypes for live-restore file-system setup, server lifecycle, turtle-file interception, metadata conversion, validation, and stats initialization.

## Important APIs, Types, and Functions
`WT_LIVE_RESTORE_STATE_STRING_MAX` bounds persisted state parsing. `WT_LIVE_RESTORE_FH_META` stores the `live_restore=(bitmap=...,nbits=...)` metadata fields plus `allocsize`; `nbits == -1` means migration for that file is complete. Prototypes include `__wt_os_live_restore_fs`, `__wt_live_restore_server_create/destroy`, `__wt_live_restore_metadata_to_fh`, `__wt_live_restore_fh_to_metadata`, `__wt_live_restore_clean_metadata_string`, `__wt_live_restore_get_state_string`, turtle wrappers, non-live-restore validation, and `__wt_live_restore_init_stats`. Under `HAVE_UNITTEST`, it exposes wrappers for bitmap encoding/decoding, bit filling, read-end computation, and hole filling.

## Control Flow
Connection setup calls `__wt_os_live_restore_fs` when `live_restore.enabled=true`, then starts the server through `__wt_live_restore_server_create`. Block open reconstructs file-handle bitmaps through `__wt_live_restore_metadata_to_fh`; checkpoints append file metadata through `__wt_live_restore_fh_to_metadata`; metadata/turtle operations use the turtle wrappers to preserve lock ordering. Shutdown calls `__wt_live_restore_server_destroy`.

## State and Persistence Behavior
The header documents the durable per-file metadata shape: a hex bitmap string, a bit count, and allocation size. State strings are persisted through turtle metadata, while file-hole state is persisted in checkpoint metadata. Backup cleanup can rewrite `nbits=-1` to `nbits=0` so a future restore source does not falsely indicate already-migrated files.

## Dependencies and Integration Points
Included by `wt_internal.h` after live-restore typedefs have been declared. The prototypes are consumed by block manager file open, checkpoint metadata code, backup cursor cleanup, metadata/turtle code, connection open/reconfigure/close paths, utility configuration, and live-restore tests.

## Risks and Edge Cases
The generated prototype section must match the implementations. The `nbits` sentinel values are subtle: `0` means not started, positive values mean a persisted bitmap exists, and `-1` means migration completed. Unit-test-only functions expose static internals and must remain guarded to avoid changing production ABI.

## Test Signals
Catch2 unit tests under `test/catch2/live_restore/unit` directly exercise the unit-test wrappers. API tests under `test/catch2/live_restore/api`, Python suite tests `test_live_restore01.py` through `test_live_restore08.py`, and `test/cppsuite/tests/test_live_restore.cpp` exercise the declared integration points.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/live_restore/live_restore.h -->

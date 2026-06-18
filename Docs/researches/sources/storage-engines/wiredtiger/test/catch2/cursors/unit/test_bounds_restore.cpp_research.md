<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/cursors/unit/test_bounds_restore.cpp -->
# sources/storage-engines/wiredtiger/test/catch2/cursors/unit/test_bounds_restore.cpp

Purpose: Tests cursor bounds flag save/restore logic.

Important APIs/types/functions: Calls `__wt_cursor_bounds_save` and `__wt_cursor_bounds_restore`; validates `WT_CURSOR::flags` against an original snapshot.

Control flow: Initializes a mock `WT_CURSOR` and `WT_CURSOR_BOUNDS_STATE`, sets upper/lower and inclusive bound flags in separate sections, saves state, restores state, and verifies flags.

State and persistence behavior: Uses scratch buffers on a real session from `connection_wrapper`; frees lower/upper bound scratch in one section.

Dependencies and integration points: Covers cursor bound state helper used by search/positioning paths.

Risks and test signals: Memory cleanup for saved bounds is important. Signals are exact preservation of inclusive and non-inclusive flag bits.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/cursors/unit/test_bounds_restore.cpp -->

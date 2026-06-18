<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/block/unit/test_extent_list_search.cpp -->
# sources/storage-engines/wiredtiger/test/catch2/block/unit/test_extent_list_search.cpp

Purpose: Tests neighbor-pair and overlap search helpers for extent lists.

Important APIs/types/functions: Calls `__ut_block_off_srch_pair` and, under `HAVE_DIAGNOSTIC`, `__ut_block_off_match`.

Control flow: Builds empty and populated extent lists, searches offsets before, at, between, and after known extents, and verifies before/after nodes. Diagnostic tests check empty, adjacent, contained, boundary, and overlapping ranges.

State and persistence behavior: Local `WT_EXTLIST` mutation and cleanup only.

Dependencies and integration points: Uses mock sessions and `utils_extlist`; overlap detection is important for diagnostic validation of free-space list consistency.

Risks and test signals: Boundary-touching ranges must not be treated as overlap unless bytes intersect. `BREAK` markers and `HAVE_DIAGNOSTIC` gating affect coverage.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/block/unit/test_extent_list_search.cpp -->

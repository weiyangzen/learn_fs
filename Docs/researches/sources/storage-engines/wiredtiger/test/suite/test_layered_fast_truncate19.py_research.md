<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate19.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate19.py

Purpose: verifies that fast truncate suppresses internal page delta writes when reconciliation sees a deleted child reference.

Important APIs/types/functions: this class derives directly from `wttest.WiredTigerTestCase`, enables `page_delta=(internal_page_delta=true,leaf_page_delta=false,delta_pct=100)`, and reads dsrc/connection stats including `rec_page_delta_rejected_invalid_page_id`, `rec_page_delta_internal`, `rec_page_delete_fast`, and `cache_read_deleted`.

Control flow: setup uses tiny page sizes to create a multi-level tree, inserts 200 rows, checkpoints, and evicts leaves. Before reopen, a normal update should reject delta due to invalid disaggregated page id. After `reopen_disagg_conn`, normal updates outside the truncation range must increase internal delta stats. Then `truncate_and_checkpoint(50,150,20)` must trigger fast delete, avoid instantiating deleted pages, and leave the internal delta counter unchanged.

State and persistence behavior: the test follows page-id assignment, fast-deleted leaf state, and internal reconciliation output across checkpoint/reopen.

Dependencies/integration points: highly dependent on page layout, eviction, page-delta feature flags, and stat counters. Risks are brittle configuration if page eligibility changes. Test signals are stat deltas, WT_NOTFOUND for truncated boundaries, and no `cache_read_deleted` increase.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate19.py -->

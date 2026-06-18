# sources/storage-engines/wiredtiger/test/suite/test_layered_delta10.py

Purpose: confirms page delta generation is suppressed when reconciliation splits a page, while a similar non-splitting update produces a leaf delta.

Important APIs and functions: `test_layered_delta10` uses split scenarios, `page_delta=(delta_pct=100,internal_page_delta=true,leaf_page_delta=true)`, small `allocation_size`, `leaf_page_max`, `split_pct`, data-source stats `btree_row_leaf` and `rec_page_delta_leaf`, and `reopen_conn`.

Control flow: the test creates one near-4KB leaf page, reopens and asserts one row leaf. In `page_split` mode it updates one row and appends more rows to exceed the split threshold, checkpoints, asserts zero leaf deltas, reopens, and expects two leaf pages. In `page_no_split` mode it only updates one row, checkpoints, expects one leaf delta, and still one leaf page.

State and persistence behavior: reconciliation has two possible outputs: a structural split requiring full page images, or a small content update eligible for delta encoding. The test distinguishes those paths through statistics and physical leaf count after reopen.

Dependencies and integration: integrates page split policy, delta generation policy, layered disaggregated tables, and data-source statistics. Risks include generating deltas across structural splits, suppressing deltas for ordinary updates, or page-size dependent fragility. Test signals are exact leaf-page and delta-count assertions.

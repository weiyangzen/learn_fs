<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_truncate14.py -->
# sources/storage-engines/wiredtiger/test/suite/test_truncate14.py

Purpose: Generates very large namespace gaps with truncate to stress instantiation and reconciliation logic over sparse key spaces.

Important APIs/types/functions: Uses `session.truncate`, `stat.conn.rec_page_delete_fast`, `SimpleDataSet`, `simulate_crash_restart` import though not used, timestamped read checks, and scenarios for action `instantiate`, `checkpoint`, and `checkpoint-visible`.

Control flow: The test writes a dense blob, then 20,000 sparse keys separated by 1,000,000,000, then another dense blob at timestamp 20. It stabilizes and reopens, truncates the sparse range at timestamp 30, checks fast-delete stats, stabilizes the truncate, validates remaining rows, and then either reads behind the truncate, checkpoints while not globally visible, or advances oldest before checkpointing. It validates remaining rows again.

State and persistence behavior: Sparse keys create huge logical gaps. The truncate deletes across the sparse namespace, and subsequent actions cover page instantiation and internal-page reconciliation before and after global visibility.

Dependencies and integration points: Integrates fast-delete key-range handling, sparse row/column namespaces, checkpoint, oldest/stable timestamps, and cursor iteration over large key gaps.

Risks: Loops over logical key ranges must not scale with key-space size. Incorrect gap handling can lose the dense boundary rows or hang during instantiation.

Test signals: Row-count checks before and after truncate plus positive fast-delete page stats.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_truncate14.py -->

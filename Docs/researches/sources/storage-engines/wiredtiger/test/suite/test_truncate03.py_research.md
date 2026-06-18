<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_truncate03.py -->
# sources/storage-engines/wiredtiger/test/suite/test_truncate03.py

Purpose: Exercises address-deleted cells produced by truncating unloaded pages, recovery, freeing deleted pages, and later instantiating empty pages.

Important APIs/types/functions: `test_truncate_address_deleted` uses `SimpleDataSet`, `reopen_conn`, `verifyUntilSuccess`, explicit checkpointing, cursor update/scan, `raisesBusy`, and `session.verify`.

Control flow: `address_deleted` creates a large small-page file, reopens and verifies, starts a long transaction to force checkpoint behavior, truncates a broad range, checkpoints address-deleted cells to disk, reopens, verifies, dirties and walks the tree, and checkpoints again to free pages. One test loops verify until not busy; the other writes into keys in the deleted range, checkpoints/reopens, verifies, and reads those values back.

State and persistence behavior: Focuses on on-disk internal-page address-deleted cells, recovery conversion to free pages, and synthetic empty-page instantiation after underlying leaf pages are removed.

Dependencies and integration points: Integrates reconciliation, checkpoint, recovery/reopen, verification, btree deleted-page handling, and row/column formats.

Risks: Bugs here can surface as verify failures, missing free-page conversion, or inability to create pages for writes into previously deleted ranges.

Test signals: Successful verify after recovery/freeing, absence of busy after checkpoints, and exact readback of newly written values in the formerly deleted range.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_truncate03.py -->

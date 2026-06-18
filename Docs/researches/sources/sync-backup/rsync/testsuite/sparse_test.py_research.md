# sources/sync-backup/rsync/testsuite/sparse_test.py

Purpose: validates `-S/--sparse` preservation for a sparse file several levels deep, while avoiding invalid assumptions about non-sparse copies on filesystems that auto-sparsify zero runs.

Important APIs and flow: imports tree helpers plus `assert_same`, `test_fail`, and `test_skipped`. `make_sparse()` writes `head`, seeks near 4 MiB, and writes `tail`. `allocated()` uses `st_blocks * 512`. The test skips if the source filesystem did not actually create a sparse file. With `rsync -a -S`, it asserts byte equality and allocated size below the apparent size. With `--no-sparse`, it only asserts byte equality.

State and persistence: source and destination trees are removed before each transfer; sparse behavior is inspected via filesystem metadata, not external tools.

Dependencies and integration: covers receiver file-writing choices, sparse-hole detection, and deep parent path handling. Risks include platform filesystems with unusual block accounting and sparse support; the skip protects the main premise. Test signal is content equality plus destination allocation below `SIZE` only for the sparse-enabled transfer.

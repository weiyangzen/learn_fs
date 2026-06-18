# sources/sync-backup/rsync/testsuite/append_test.py

Purpose: depth coverage for `--append` and `--append-verify`, including their semantic split at protocol >= 30.

Important APIs/types/functions: `make_tree`, `walk_files`, `forced_protocol`, `dest_prefix`, `run_rsync`, `assert_same`, and `test_fail`.

Control flow: build a depth-3 data tree, create destination prefixes for every file, and verify `--append` completes them. If protocol is not forced below 30, corrupt the deep file prefix and show plain `--append` leaves it wrong, while `--append-verify` repairs it.

State and persistence behavior: destination files are partial prefixes; the deep file can have corrupted leading bytes. The test asserts tail-only completion and verification-driven redo behavior.

Dependencies and integration points: append receiver/generator paths, protocol feature gating, and deep file traversal.

Risks and test signals: old protocol behavior skips distinguishing cases. Failures indicate incorrect trust/verification split or broken append repair at depth.

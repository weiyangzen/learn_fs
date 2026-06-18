# sources/sync-backup/rsync/testsuite/compare_test.py

Purpose: depth coverage for file comparison and skip options: default quick check, `-c`, `-I`, `--size-only`, and `--modify-window`.

Important APIs/types/functions: `seed`, `stealth_change`, `samesize_newmtime`, `run_rsync`, `assert_same`, and dry-run itemization checks.

Control flow: build and copy a depth-3 data tree. Create same-size same-mtime content changes and prove default quick check skips them, while checksum and ignore-times catch them. Then prove `--size-only` skips a same-size file even with changed mtime, while default catches it. Finally use dry runs to show `--modify-window=2` absorbs a one-second mtime difference.

State and persistence behavior: manipulates deep file content and mtimes to target selection decisions without changing path structure.

Dependencies and integration points: rsync generator quick-check logic, checksum comparison, size-only selection, modify-window itemization, and harness assertions.

Risks and test signals: timing is controlled via explicit `os.utime`. Failures distinguish wrong transfer selection from bad content copying.

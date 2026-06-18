# sources/sync-backup/rsync/testsuite/size-filter_test.py

Purpose: verifies `--max-size` and `--min-size` filtering across nested directories. The test ensures file-size filters apply consistently at each depth rather than only to top-level entries.

Important APIs and flow: imports `FROMDIR`, `TODIR`, `assert_not_exists`, `assert_same`, `make_data_file`, `rmtree`, and `run_rsync`. `seed()` rebuilds a four-level tree, placing `smallN` and `largeN` files at every level. The first pass runs `rsync -a --max-size=1000` and asserts each small file is byte-identical while each large file is absent. The second pass reseeds and runs `--min-size=1000`, asserting the inverse.

State and persistence: fixture state is fully recreated for each half, eliminating stale-output false positives. File sizes are deterministic constants (`500` and `5000` bytes).

Dependencies and integration: exercises option parsing and receiver/generator selection for per-file transfer decisions. It also indirectly covers recursive flist traversal. Risks are mostly harness-level: `assert_same` must compare content, and destination cleanup must be reliable. Test signal is precise absence/presence plus content equality at all four levels.

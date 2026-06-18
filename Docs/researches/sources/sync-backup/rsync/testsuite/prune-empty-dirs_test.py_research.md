## sources/sync-backup/rsync/testsuite/prune-empty-dirs_test.py

Purpose: verifies `-m`/`--prune-empty-dirs` removes directory chains that are empty in the source or become empty after filtering.

Important APIs and control flow: `reseed()` clears source and destination. First fixture creates an empty deep chain and a populated deep chain; `rsync -a -m` must omit `empty` and keep the file under `full`. Second fixture creates mixed keep/drop files and a logs-only subtree; with `--exclude=*.log`, rsync must keep the mixed subtree's `.txt` file and prune `onlylogs`.

State and dependencies: uses `makepath`, `rmtree`, `run_rsync`, and existence/content assertions.

Integration points: covers sender/receiver pruning decisions after filter evaluation.

Risks and test signals: simple and robust. Path-specific absence/presence assertions prove both empty-source and filter-emptied behavior.

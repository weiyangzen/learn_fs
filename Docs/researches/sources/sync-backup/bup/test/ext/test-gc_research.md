## sources/sync-backup/bup/test/ext/test-gc

Purpose: tests garbage collection preservation and pruning across normal, rewritten, remote, and threshold/ignore-missing scenarios.

Important control flow: verifies unchanged repos remain restorable, removed branch data is pruned, rewritten branches keep reachable data, remote save/get after GC works, `bup on -` workflows survive GC, `--threshold 0` rewrites packs without losing objects, and `--ignore-missing` reports missing source objects while still rewriting eligible packs.

State and dependencies: repeatedly recreates repos, removes refs manually, measures data size, uses remote `-:repo`, `bup get`, `bup rm --unsafe`, Git show-index, and `dev/perforate-repo`.

Risks covered: reachability accounting, remote pack reuse after GC, object identity preservation under repacking, and missing-object handling during collection.

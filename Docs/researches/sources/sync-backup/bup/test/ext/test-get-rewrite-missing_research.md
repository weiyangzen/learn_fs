## sources/sync-backup/bup/test/ext/test-get-rewrite-missing

Purpose: comprehensive rewrite/repair regression test for missing files, directories, chunked files, split trees, repair IDs, and contextual command combinations.

Important control flow: builds a repo with ordinary missing objects, a chunked partial file, and a split tree, records relevant oids, drops selected objects, and validates invalid option combinations. `repair-to-dest()` runs `bup get --repair`; the test verifies repair-id reporting, commit trailers, replacement blob contents for missing files/trees/chunked files, split-tree top/leaf/bupm repairs, behavior differences between `--rewrite`, `--repair`, `--copy`, and `--ignore-missing`, multiple repair IDs, and trailer non-accumulation across repaired saves.

State and dependencies: heavily mutates repos and object stores, uses split-tree config, Git plumbing, `dev/make-splittable-tree`, `dev/perforate-repo`, and `bup get`.

Risks covered: this is the strongest signal for `rewrite.py`, `tree.py`, and VFS repair semantics. It guards against unsafe reuse of missing-object conversions, context leakage, incorrect replacement content, and trailer accumulation.

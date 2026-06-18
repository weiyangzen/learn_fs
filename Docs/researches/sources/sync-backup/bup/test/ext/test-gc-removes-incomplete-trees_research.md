## sources/sync-backup/bup/test/ext/test-gc-removes-incomplete-trees

Purpose: regression test ensuring GC does not leave reusable incomplete split trees.

Important control flow: creates a save arranged across two packfiles with held, transient, and straddling trees. It copies a complete repo, promotes one subtree, removes the original branch, runs GC with a threshold, then fetches the original back from the complete repo and verifies `bup join` succeeds.

State and dependencies: manipulates pack size limit, branch refs, `bup get --append`, `bup rm --unsafe`, and GC. Uses object location checks with `git show-index`.

Risks covered: probabilistic pack retention must not keep parent split-tree fragments without required child objects, because later get/rewrite code may otherwise reuse broken trees.

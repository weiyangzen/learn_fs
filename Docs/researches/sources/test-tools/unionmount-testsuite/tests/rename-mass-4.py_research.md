# sources/test-tools/unionmount-testsuite/tests/rename-mass-4.py

Purpose: verifies mass circular renames of newly created regular files. Unlike `rename-mass-3.py`, it creates the ring entries through the union mount before performing rename churn.

Important APIs and functions: exports `subtest_1(ctx)` and `subtest_2(ctx)`. It uses `ctx.no_file()`, `ctx.open_file(..., wo=1, crt=1, write=...)`, `ctx.rename()`, and `ctx.unlink()`.

Control flow: `subtest_1` creates all ring names with unique payloads, then rotates the gap backward through `iter_count`. `subtest_2` computes the missing slot after rotation and removes all surviving names.

State and persistence: created files live in the writable layer; after rotation their path identities change but data should remain bound to the moved inodes. Cleanup verifies dentry removal semantics.

Dependencies and integration: depends on harness path factories and open/rename wrappers. It targets union filesystem upper-layer rename behavior rather than lower copy-up behavior.

Risks: the test does not read file contents after the mass rename, so it catches namespace breakage and cleanup failures more directly than payload transposition.

Test signals: all creates and renames must succeed; cleanup must see one expected absent slot and no unexpected survivors.

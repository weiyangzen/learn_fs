# sources/test-tools/unionmount-testsuite/tests/rename-mass-5.py

Purpose: stresses circular renames across hardlinked file names, mixing a lower regular-file base and newly created hardlinks. It checks link-count/dentry consistency under repeated rename.

Important APIs and functions: defines `subtest_1(ctx)` to create hardlinks with `ctx.link()` and perform two rename cycles, and `subtest_2(ctx)` to unlink both hardlink and source namespaces.

Control flow: first it hardlinks `src_base + number` to `base + number`, then rotates the hardlink names backward. It then rotates source names forward. Cleanup calculates separate expected gaps for the two rings.

State and persistence: the relevant persistent state is shared inode identity across renamed hardlink names. The file keeps no local persistent state, so correctness is inferred from syscall outcomes.

Dependencies and integration: depends on preexisting regular fixtures, harness hardlink support, and overlayfs behavior for linked lower files and copied-up hardlinks.

Risks: cleanup loops use `ring_size + 1`, while rename loops rotate only modulo `ring_size`; this intentionally includes an extra linked name but makes gap math subtle.

Test signals: hardlink creation, both rename cycles, and unlink cleanup must match expected `ENOENT` only at computed gaps.

# sources/sync-backup/restic/internal/walker/walker_test.go

Purpose: provides reusable in-memory tree builders and tests the walker traversal contract.

Important APIs/types/functions: `TestTree`, `TestFile`, `BuildTreeMap`, `buildTreeMap`, and check factories for item order, parent tree IDs, skips, and callback errors.

Control flow: `BuildTreeMap` sorts names to produce deterministic tree hashes. `TestWalker` defines several tree shapes, runs each check against `Walk`, and validates callback order and error propagation.

State and persistence: in-memory `data.TestTreeMap` only; generated hashes simulate repository tree IDs.

Dependencies/integration: depends on restic `data` builders, `restic.ID`, and test helpers.

Risks: tests depend on exact hash values for parent tree IDs, so builder serialization changes require fixture updates.

Test signals: broad coverage for root visit, directory leave callbacks, deterministic traversal, skip-root/skip-directory/skip-file semantics, empty directories, nested directories, and callback-originated errors.

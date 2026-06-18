# sources/sync-backup/restic/cmd/restic/cmd_cat_test.go

Purpose: unit tests for `restic cat` argument validation.

Important tests: `TestCatArgsValidation` verifies missing type, accepted `masterkey`, invalid type errors, missing snapshot ID, and accepted snapshot ID shape.

State/dependencies: no repository is opened; it calls `validateCatArgs` directly and checks error substrings with `rtest`.

Risks/test signals: protects only CLI validation, not repository object output. Raw pack/blob/tree behavior remains covered by broader integration/manual use rather than this file.

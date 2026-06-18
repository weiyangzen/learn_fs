# sources/sync-backup/syncthing/cmd/infra/ursrv/serve/compiler_test.go

Purpose: validates parsing of compiler and builder identity from Syncthing long version strings used in usage report enrichment.

Important APIs/tests: `TestCompilerRe` applies package regex `compilerRe` to historical version string examples and asserts captured compiler and builder values.

Control flow and state: table-driven test iterates three samples, verifies match count, then compares capture groups.

Dependencies/integration: depends on `compilerRe` from `serve.go` and `testing`.

Risks and test signals: gives regression coverage for release string formats from older Syncthing versions. It does not cover distribution classification, version transformation, or report validation.

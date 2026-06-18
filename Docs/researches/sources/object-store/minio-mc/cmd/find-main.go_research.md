# sources/object-store/minio-mc/cmd/find-main.go

Purpose: Defines `mc find` CLI flags, validates targets, parses typed options, and constructs `findContext`.

Important APIs/types/functions: `findFlags`, `findCmd`, `checkFindSyntax`, `findContext`, and `mainFind`.

Control flow: Validation defaults no args to `./`, normalizes `.`, rejects empty args, stats inputs, and allows alias-only object storage except in watch mode. `mainFind` parses encryption, size thresholds, versions, alias expansion, regex, metadata/tag regex maps, and delegates to `doFind`.

State and persistence: Builds in-memory search context only.

Dependencies/integration: Uses client stat/init, `humanize.ParseBytes`, `validateAndCreateEncryptionKeys`, alias expansion, and find execution helpers.

Risks: `regexp.MustCompile` on `--regex` panics on invalid regex instead of returning a controlled fatal error. Only the first target is used to construct the client/context.

Test signals: `find_test.go` covers downstream matching and substitutions, not CLI parsing.

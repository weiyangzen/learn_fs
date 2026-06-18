# sources/storage-engines/pebble/internal/devtools/roachvet/forbidden_imports.go

## Purpose
`forbidden_imports.go` defines a `go/analysis` analyzer used by Pebble’s roachvet tooling to prevent selected public/top-level packages from directly or transitively importing forbidden packages.

## Important APIs, Types, And Functions
`packagesToCheck` limits analysis to `github.com/cockroachdb/pebble`, `github.com/cockroachdb/pebble/sstable`, and `github.com/cockroachdb/pebble/cmd/pebble`. `forbiddenPackages` currently forbids `testing`. `ForbiddenImportsAnalyzer` is the exported analyzer. `checkDirectImports` reports non-test files importing forbidden packages. `checkTransitiveImports` loads package dependencies and recursively reports forbidden dependency paths. `run` gates analysis to the selected packages.

## Control Flow
The analyzer first scans AST imports for direct violations, skipping `_test.go`. It then calls `packages.Load` for the analyzed package, recursively walks imports with a visited set, skips `_test` package paths, and reports a formatted chain when it reaches a forbidden package.

## State And Persistence Behavior
The analyzer has static maps only. It does not persist state. `packages.Load` observes the module/workspace at analysis time and may perform expensive dependency loading.

## Dependencies And Integration Points
It integrates with `unitchecker` in `main.go` and Go vet-style execution. Dependencies include `go/ast`, `go/token`, `x/tools/go/analysis`, and `x/tools/go/packages`.

## Risks And Edge Cases
The comment has a typo (“dirctly”) but no behavioral impact. Transitive reports use `token.NoPos`, so diagnostics may not be anchored to import statements. Loading dependencies inside an analyzer can be expensive or sensitive to build tags. The package allowlist means internal packages can import `testing` unless they leak into checked packages.

## Test Signals
Coverage is likely through CI vet invocations. Good signals are failing diagnostics for direct `testing` imports and formatted transitive chains from checked public packages.

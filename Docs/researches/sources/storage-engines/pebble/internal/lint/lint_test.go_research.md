# sources/storage-engines/pebble/internal/lint/lint_test.go

## Purpose
This file defines Pebble's repository-level lint test. It is not a library lint package; it is an integration test that shells out to Go tooling, CockroachDB-specific developer tools, and grep-based source checks to enforce project style and correctness rules across `github.com/cockroachdb/pebble/...`.

## Important APIs, Types, And Functions
`TestLint` is the central test. It resolves the module root with `build.Import`, lists all packages with `go list ./...`, runs `go vet` first, and then runs several independent subtests. `dirCmd` executes a command in a directory and exposes combined output as a `stream.Filter`, treating non-zero exit codes as expected lint output rather than immediate test failure. `ignoreGoMod` filters noisy module download lines. `installTool` installs tools from `../devtools` through `go install -C`. `lintIgnore` consumes paired grep context lines and drops findings preceded by a specific ignore directive.

## Control Flow
The test skips on Windows, 386, and slow/instrumented builds. `TestGoVet` runs first and aborts the remaining lint suite if it fails, reducing noise from build failures. The rest of the subtests use `t.Parallel` where safe: `gcassert`, `staticcheck`, custom `roachvet`, grep checks for panic arguments, `fmt.Errorf`, `os.Is*`, `runtime.SetFinalizer`, raw atomics, forbidden imports, and `crlfmt`. Several checks build a `stream.Sequence` pipeline that runs a command, filters lines, and reports remaining lines as test errors.

## State, Persistence, And Side Effects
The test has no persisted application state, but it mutates the developer environment by installing lint tools into the active Go tool bin. It shells out to `git grep`, `go list`, `go vet`, and format/lint binaries, so behavior depends on the working tree, module cache, and available toolchain. The `crlfmt` subtest only reports formatting drift and logs a rewrite command; it does not modify files.

## Dependencies And Integration Points
The file depends on `github.com/ghemawat/stream` for stream processing, `testify/require`, `go/build`, `os/exec`, Pebble build tags, CockroachDB errors, and the tools declared by import path constants. It integrates with Pebble's `internal/devtools` module, the root Go module, Git, and repository-specific lint conventions like `lint:ignore PanicArgs`, `lint:ignore SetFinalizer`, and `lint:ignore RawAtomics`.

## Risks And Edge Cases
The lint suite is intentionally environment-sensitive. Missing tools, path issues, or module-cache/network problems can fail the test before source issues are evaluated. `lintIgnore` assumes `git grep -B1` emits exact pairs of directive and finding lines; changing grep context could make ignores unreliable. The forbidden import check loads packages with `UseAllFiles`, falling back for multiple-package directories, so generated/build-tag-only imports may still need care. The raw regex checks are broad and require explicit ignore directives for legitimate exceptions.

## Test Signals
This file is itself the test signal. Passing `go test ./internal/lint` indicates the repository builds under `go vet`, static analysis tools run cleanly, CockroachDB formatting is satisfied, and banned APIs/imports are absent except where ignored. Failures are line-oriented and intended to be clickable in IDEs.

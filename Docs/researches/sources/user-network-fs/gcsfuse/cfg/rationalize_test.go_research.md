# sources/user-network-fs/gcsfuse/cfg/rationalize_test.go

## Purpose
`rationalize_test.go` verifies the package-level behavior of `cfg.Rationalize` and selected helper functions. It focuses on final in-memory config values after defaults, explicit Viper settings, deprecated fields, optimization flags, and cross-feature conflicts have been accounted for.

## Important APIs And Test Structure
The file uses Go table-driven tests with `testing`, `testify/assert`, and `testify/require`. It directly constructs `cfg.Config` values and Viper instances, then calls `Rationalize` or helper functions. Major tests include custom endpoint and token URL success/failure, GCS retry max-attempt expansion, read global block sentinel expansion, logging severity override from debug flags, metadata cache TTL/stat-cache size precedence, optimization-aware metadata cache behavior, streaming write rationalization, metrics interval migration, trace exporter trimming/lowercasing, parallel-download defaulting, file-cache versus buffered-read conflict handling, log format fallback, and metadata prefetch sentinel expansion.

## Control Flow And State
Each test case mutates a fresh config object and checks the resulting fields. Some cases populate Viper with keys purely to make `v.IsSet` true, which models explicit user settings. The buffered-read conflict test temporarily redirects the standard logger to a bytes buffer and restores it afterward, so it also verifies warning emission when the user explicitly requested buffered reads. There is no persistence beyond temporary log capture.

## Dependencies And Integration
The tests exercise the same cfg package that `cmd/root.go` invokes after validation and optimization. They also indirectly document contracts consumed by `cmd/mount.go` and `cmd/legacy_main.go`, such as `MaxRetryAttempts == math.MaxInt` for unlimited retries, metadata TTL `-1` becoming max supported seconds, file cache enabling parallel downloads unless explicitly set, and streaming writes disabling `CreateEmptyFile`.

## Risks And Test Signals
The suite is a strong signal for precedence-sensitive code, but it mostly bypasses generated defaults and command unmarshalling. That gap is covered by command-level rationalization tests. A risk in the tests is reliance on exact Viper keys; if config aliases change, package tests may continue to pass while CLI behavior changes. The tests intentionally encode compatibility for deprecated stat/type cache fields, debug flags forcing TRACE, and default-on parallel downloads with file cache.

# sources/object-store/minio/cmd/main.go

## Purpose

`main.go` builds and runs the MinIO CLI application. It defines global flags, help/version output, command registration, typo suggestions for unknown commands, startup banners, and the debug no-exit mode used for diagnostics.

## Important APIs, Control Flow, And State

`GlobalFlags` declares hidden legacy config/compat flags and visible certs-dir, quiet, anonymous, json, plus hidden no-compat. `minioHelpTemplate` customizes CLI help. `newApp` registers build-enabled commands (`serverCmd` and `fmtGenCmd`) into both a slice and trie, configures help/version behavior, metadata, flags, commands, and a `CommandNotFound` handler. Unknown command suggestions combine trie prefix matches with Damerau-Levenshtein distance less than 2 and then exit.

`startupBanner` writes copyright, license, release tag, Go version, OS, and architecture, updating `CopyrightYear` to the current year. `versionBanner` returns an `io.Reader` with version, commit ID, runtime, license, and copyright. `printMinIOVersion` copies that reader to the CLI writer. `debugNoExit` is controlled by `_MINIO_DEBUG_NO_EXIT`; when enabled, `Main` overrides `logger.ExitFunc`, recovers panics to stdout with stack, then blocks forever. Otherwise `Main` derives the app name from `args[0]`, runs the CLI app, and exits with status 1 on errors.

State is global CLI/logger configuration and environment-driven debug mode. Dependencies include `minio/cli`, console/color helpers, env, trie, words, runtime/debug, and command globals.

## Risks And Test Signals

Risks include `args[0]` assumptions, unknown-command suggestion ordering, hidden flag compatibility, global mutation in debug mode, and immediate process exits complicating tests. No direct tests in this subset cover `newApp` or `Main`; behavior is generally exercised by CLI integration tests.

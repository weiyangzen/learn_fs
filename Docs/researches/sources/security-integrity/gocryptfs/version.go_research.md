# sources/security-integrity/gocryptfs/version.go

## Purpose
Implements gocryptfs version reporting, combining build-time linker variables, Go build-info fallback, feature tags, go-fuse dependency version, build date, race detector status, and target platform.

## Important APIs, Types, And Functions
- `GitVersion`, `GitVersionFuse`, and `BuildDate` are build-time variables with sentinel defaults.
- `init` calls `versionFromBuildInfo` before main code uses version fields.
- `printVersion` formats and prints the user-facing version line.
- `versionFromBuildInfo` reads module build metadata and fills unset version fields.
- `raceDetector` is set by a separate race-build file when compiled with `-race`.

## Control Flow
At startup, build-info fallback runs only for unset linker fields. `printVersion` then derives optional tags such as `without_openssl`, appends `-race` when relevant, and prints program name, gocryptfs version, go-fuse version, build date, Go runtime version, OS, and architecture.

## State And Persistence
State is process-global version variables set either by build scripts or Go module metadata. No persistent files are touched.

## Dependencies And Integration Points
Depends on `runtime/debug.ReadBuildInfo`, `internal/stupidgcm` for OpenSSL tag reporting, and `internal/tlog.ProgramName`.

## Risks And Edge Cases
Fallback build info may be unavailable or `(devel)`, leaving sentinel strings if build scripts did not inject values. Replacement modules with empty replacement versions can affect go-fuse version output.

## Test Signals
Test signals are indirect: CLI `--version` output should include expected build/version metadata and tags for the binary build mode.

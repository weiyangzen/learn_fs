# sources/storage-engines/tikv/scripts/check-docker-build

## Purpose
Ensures tracked Cargo manifests explicitly specify `path =` for `test`, `bench`, `bin`, and `example` targets so Docker builds do not rely on implicit Cargo path inference.

## Important Commands and Control Flow
The script enumerates tracked `Cargo.toml` files except fuzz manifests with `git ls-files`. For each target kind, it extracts each target table range using `sed` and compares the number of `[[target]]` headers with the number of `path =` lines. A mismatch prints the manifest and exits 1; otherwise it prints `Docker build check passed.`

## State, Dependencies, Integration
No state is written. It depends on Git, grep, sed, bash, and conventional Cargo manifest formatting. It integrates with Docker-build preflight checks.

## Risks and Test Signals
The TOML parsing is textual and can be confused by blank lines, comments, or unusual formatting. It only checks tracked files. A manifest target without explicit `path =` should fail the script; all compliant manifests should exit 0.

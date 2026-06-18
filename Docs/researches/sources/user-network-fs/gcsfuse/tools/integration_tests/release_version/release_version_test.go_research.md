# sources/user-network-fs/gcsfuse/tools/integration_tests/release_version/release_version_test.go

## Purpose

This test validates the user-visible `gcsfuse --version` output format for release builds.

## Important APIs, Types, and Functions

`TestReleaseVersion` runs `exec.Command("gcsfuse", "--version")`, captures combined output, trims whitespace, and matches it against the regexp `^gcsfuse version (\d+\.\d+\.\d+) \(Go version (go.+)\)$`. It extracts and checks non-empty gcsfuse and Go versions.

## Control Flow

The test executes the binary, fails immediately if command execution fails, logs the output for debugging, applies the regexp, and reports detailed mismatch information if the shape is wrong.

## State and Persistence Behavior

No filesystem or bucket state is mutated by the test itself. It depends on the active `gcsfuse` binary in `PATH`, which is set up by package harness or external test environment.

## Dependencies and Integration Points

It uses standard `os/exec`, `regexp`, `strings`, and `testing`. It integrates with the release-version harness that prepares the test environment but does not mount a bucket.

## Risks and Edge Cases

The regexp requires three numeric semver components and exact text casing/parentheses. Pre-release/build metadata, distro suffixes, or alternate Go version formatting would fail. The test validates format, not that the version matches a release tag.

## Test Signals

Passing means the installed or built binary prints a release-style version line with both gcsfuse and Go versions. Failure is a packaging/build metadata or CLI output regression.

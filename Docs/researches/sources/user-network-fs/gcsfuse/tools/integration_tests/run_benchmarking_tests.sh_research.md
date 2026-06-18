# sources/user-network-fs/gcsfuse/tools/integration_tests/run_benchmarking_tests.sh

## Purpose

This short script documents and runs the benchmarking integration test package with a fixed bucket and benchmark iteration count.

## Important APIs, Types, and Functions

It invokes `GODEBUG=asyncpreemptoff=1 go test ./tools/integration_tests/benchmarking/... -bench=. -benchtime=5x --integrationTest -v --testbucket=princer-empty-bucket`.

## Control Flow

There is no argument parsing or function dispatch. Running the script immediately starts the benchmark package with all benchmarks enabled and each benchmark run five times.

## State and Persistence Behavior

The script does not create explicit state itself, but the benchmark package will mount/use the hard-coded bucket and may create objects depending on benchmark implementation. It relies on the current environment for credentials and GCSFuse binary selection.

## Dependencies and Integration Points

It depends on Bash, Go tooling, the integration test benchmark package, and access to the hard-coded bucket. `GODEBUG=asyncpreemptoff=1` aligns with other integration runners for timing stability.

## Risks and Edge Cases

The hard-coded bucket makes the script environment-specific. There is no `set -e`, no usage text, and no way to pass bucket, timeout, or installed-package flags. It is best treated as an example rather than the main CI harness.

## Test Signals

Benchmark output from `go test` is the primary signal. Failures likely indicate missing credentials, unavailable bucket, package build failures, or benchmark regressions.

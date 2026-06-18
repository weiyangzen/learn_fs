# sources/user-network-fs/rclone/bin/test-repeat.sh

Purpose: generic helper for repeatedly running a compiled Go test binary to catch flaky tests. It accepts iteration count, binary name, log prefix, `-race`, `-tags`, and passes other flags to the test binary.

Control flow parses flags manually, compiles with `go test -c`, then loops `seq -w` iterations, writing each run's output to a log and deleting logs for successful runs. State changes are the test binary and failure log files. Dependencies are bash and Go. Risks include simplistic option parsing, unquoted expansions, logs accumulating on frequent failures, and treating unknown `--flag=value` by stripping before pass-through. Test signal is per-iteration OK/FAIL plus retained logs.

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/observability_flags_test.go -->
# sources/sync-backup/kopia/cli/observability_flags_test.go

## Purpose
Tests observability CLI flags for Prometheus push gateway behavior, OTLP flag handling, and metrics save-on-exit output.

## Important APIs, Types, And Functions
Defines `TestMetricsPushFlags`, `TestOTLPFlags`, and `TestMetricsSaveToOutputDirFlags`. It uses `httptest.Server`, in-process CLI runs, temporary directories, and captured HTTP request bodies/auth.

## Control Flow
The push test creates a repo and runs status with push flags, expecting initial and final pushes, grouping path segments, basic auth, and metrics body content. It also asserts invalid grouping syntax fails. OTLP test checks a deprecated flag failure and that `--otlp-trace` does not require a running collector for the crypto benchmark. Metrics save test verifies one diagnostics subdirectory is created.

## State And Persistence Behavior
Persistent test state includes temporary repositories and diagnostics directories. Network state is local httptest only.

## Dependencies And Integration Points
Integrates CLI command execution, Prometheus pusher, metrics gatherer, auth/grouping flags, and diagnostics output.

## Risks And Edge Cases
Assertions depend on push ordering and metric names such as `kopia_cache_hit_bytes_total`. Concurrent metrics can make bodies large but should include stable names.

## Test Signals
Good regression signal for observability flag plumbing and start/stop behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/observability_flags_test.go -->

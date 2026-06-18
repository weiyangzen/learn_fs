<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/negative_stat_cache/finite_int_negative_stat_cache_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/negative_stat_cache/finite_int_negative_stat_cache_test.go

## Purpose

This suite verifies finite negative stat cache behavior. With a finite negative TTL, a missing-file lookup should remain cached briefly after the object appears in GCS, then refresh after the TTL expires.

## Important APIs, Types, and Functions

`finiteNegativeStatCacheTest` mirrors the disabled suite with per-test randomized directory state. `TestFiniteNegativeStatCache` uses `operations.CreateDirectory`, `os.OpenFile`, `client.CreateObjectInGCSTestDir`, and `time.Sleep`.

## Control Flow

The test creates an explicit directory and attempts to open a missing file, expecting no-such-file. It then creates the object directly in GCS, immediately opens the file again and still expects no-such-file because the finite negative cache should answer. After sleeping 5 seconds, it opens again and expects success.

## State and Persistence Behavior

The behavior under test is negative metadata cache state inside gcsfuse. Direct GCS insertion creates divergence from the cached miss. The sleep duration is intended to cross the configured negative cache TTL.

## Dependencies and Integration Points

It depends on package setup selecting a finite negative stat cache TTL and shared mount/client utilities. It complements the disabled-cache test to validate both immediate refresh and stale-negative behavior.

## Risks and Test Signals

Timing is the main risk; the test assumes 5 seconds is enough for expiry. Error-string assertions are path-sensitive. Passing signals are miss, cached miss after remote creation, and successful open after TTL expiry.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/negative_stat_cache/finite_int_negative_stat_cache_test.go -->

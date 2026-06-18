# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/TestReconUtils.java

## Purpose
This JUnit test covers utility methods in `ReconUtils`, including Recon DB directory resolution, tar creation/extraction, HTTP checkpoint download plumbing, latest DB selection, and power-of-two bucket index calculation.

## Important APIs and functions
`testGetReconDbDir` checks config-to-`File` resolution. `testCreateTarFile` writes two files and calls `ReconUtils.createTarFile`. `testUntarCheckpointFile` creates a tar and extracts it with `untarCheckpointFile`. `testMakeHttpCall` mocks `URLConnectionFactory` and `HttpURLConnection` to verify returned input stream contents. `testGetLastKnownDB` confirms prefix-based latest file selection. `testNextClosestPowerIndexOfTwo` compares `ReconUtils.nextClosestPowerIndexOfTwo` against a fixed reference for zero, powers, neighbors, extremes, and random values. `getContainer` is a public static fixture helper for building `ContainerInfo`.

## Control flow, state, and persistence
Tests use JUnit `@TempDir` filesystem state and clean up tar artifacts. The HTTP test is fully mocked and does not perform network I/O. The power-index test exercises many branches, including negative values and `Long.MIN_VALUE`.

## Dependencies and integration points
Dependencies include Apache Commons IO, Hadoop `URLConnectionFactory`, SCM `ContainerInfo`, `RatisReplicationConfig`, and JUnit temp directories. `getContainer` can be reused by other tests needing simple container fixtures.

## Risks and edge cases
Tar tests validate successful extraction count but not path traversal hardening, permissions, nested directories, or corrupt tar behavior. `testGetLastKnownDB` relies on filesystem listing/order behavior only through the utility. Random values improve coverage but are not deterministic.

## Test signals
Good utility-level coverage for common success paths and regression coverage for signed power-index behavior. Security-sensitive tar extraction should have additional malicious-archive tests if not elsewhere covered.

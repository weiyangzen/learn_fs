# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/client/TestOzoneQuota.java

## Purpose
`TestOzoneQuota` verifies a boundary case in quota construction: zero-byte quota values should remain zero instead of being inflated or assigned an inappropriate unit.

## APIs and dependencies
The test calls `OzoneQuota.getOzoneQuota(0, 1)` and checks `getQuotaInBytes`, `getRawSize`, and `getUnit`. It depends only on JUnit Jupiter and `OzoneQuota`.

## Control flow and state behavior
The single test method is pure and has no persistent state. It constructs a quota from a byte count of zero and a replication factor of one, then asserts both logical quota and raw size are zero and the unit is `OzoneQuota.Units.B`.

## Integration points
Ozone quota values affect volume and bucket accounting, display, and enforcement. This boundary condition protects callers that use zero to mean an exact zero value or a special configured state rather than one byte, one kilobyte, or an unset quota.

## Risks and test signals
Quota normalization code can easily mishandle zero while selecting human-readable units. This test gives a narrow but important signal that zero remains stable through quota construction and raw-size calculation.

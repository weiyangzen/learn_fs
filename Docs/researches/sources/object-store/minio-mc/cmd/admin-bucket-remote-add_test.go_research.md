<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-bucket-remote-add_test.go -->
# sources/object-store/minio-mc/cmd/admin-bucket-remote-add_test.go

## Purpose
Unit test coverage for bandwidth string parsing used by replication/remote bucket configuration helpers.

## Important APIs, types, and functions
`TestGetBandwidthInBytes` table-tests `getBandwidthInBytes` with decimal SI units (`M`, `G`), binary IEC units (`Mi`, `Gi`, `Ki`), fractional values, very large values, and small values.

## Control flow
The test runs in parallel and iterates cases, failing if parsing returns an error or a byte count different from the expected integer.

## State and persistence behavior
No state or persistence. It validates pure parsing behavior.

## Dependencies and integration points
Targets helper logic used by bucket remote/replication configuration even though surrounding admin remote commands are deprecated wrappers.

## Risks and test signals
Float truncation/rounding is the main risk for fractional units. The table is the direct signal for expected decimal-vs-binary semantics.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-bucket-remote-add_test.go -->

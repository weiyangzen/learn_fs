# sources/user-network-fs/rclone/lib/diskusage/diskusage_test.go

## Purpose
This file provides a platform-generic smoke test for `diskusage.New`.

## Important APIs, types, and functions
- `TestNew` calls `New(".")`, skips on `ErrUnsupported`, logs fields, and asserts basic size relationships.

## Control flow
The test probes the current working directory. Unsupported platforms are explicitly skipped. Supported platforms must return no error, a nonzero total, total greater than free and available, and free greater than or equal to available.

## State and persistence behavior
No persistent state is changed. The test reads live filesystem statistics.

## Dependencies and integration points
The test uses `testify/assert` and `testify/require`, and integrates with whichever build-tagged `New` implementation is compiled.

## Risks and edge cases
The assertion `Total > Free` may fail on unusual or synthetic filesystems that report an empty filesystem as all free, and live filesystem stats can vary. The test is intentionally a smoke test rather than exact accounting.

## Test signals
It confirms the compiled platform implementation can query the local filesystem and returns internally consistent byte counts, or that the platform cleanly reports `ErrUnsupported`.

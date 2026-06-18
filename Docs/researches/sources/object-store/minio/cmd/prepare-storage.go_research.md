# sources/object-store/minio/cmd/prepare-storage.go

## Purpose
This file prepares erasure storage during startup: logging endpoint errors, cleaning temporary metadata, resolving peer liveness, loading or initializing `format.json`, and waiting for quorum.

## Important APIs, Types, and Functions
`printEndpointError` rate-limits repeated endpoint logs. `bgFormatErasureCleanupTmp` renames old temp buckets, creates deleted-temp metadata, removes writable-check leftovers, and schedules metacache cleanup. `isServerResolvable` performs peer liveness checks. `connectLoadInitFormats` loads all disk formats, handles fatal disk errors, validates format values, initializes fresh disks when appropriate, and returns the quorum format. `waitForFormatErasure` initializes storage disks and loops until format quorum is available or startup is stopped.

## Control Flow and State
Startup first creates disk handles, then repeatedly calls `connectLoadInitFormats`. Fresh clusters distinguish first disk from later disks with `errNotFirstDisk` and `errFirstDiskWait`. On success, the deployment ID is stored globally and pushed into HTTP metadata.

## Dependencies and Integration Points
The code depends on storage disk initialization, erasure format helpers, global endpoints, internode transport, logger, OS signal channel, and reliable filesystem wrappers from this subset.

## Risks and Test Signals
Startup correctness depends on precise quorum and error classification. Wrong initialization on partially available disks can corrupt cluster membership, while over-fatal errors can block recovery. This subset has no direct tests; coverage likely comes from erasure startup and format tests elsewhere.

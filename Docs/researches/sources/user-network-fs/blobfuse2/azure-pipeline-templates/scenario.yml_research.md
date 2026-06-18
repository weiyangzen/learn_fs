# sources/user-network-fs/blobfuse2/azure-pipeline-templates/scenario.yml

## Purpose
This template runs targeted Go filesystem scenario tests against normal and direct-IO Blobfuse2 mounts.

## Important APIs, Types, and Functions
It generates file-cache or block-cache configs, creates a second local temp mountpoint `$(WORK_DIR)/t1`, mounts with `mount.yml`, and runs `go test -v ./test/scenarios -mountpoints="$(MOUNT_DIR),$(WORK_DIR)/t1"` with optional `-mount-point-direct-io=true`.

## Control Flow
After config generation and temp directory creation, it mounts normally and runs the scenario suite comparing/using the Blobfuse2 mount and local path. It then remounts with `-o direct_io` and reruns the scenario suite with the direct-IO flag.

## State and Persistence Behavior
It writes scenario data into both the Blobfuse2 mount and `$(WORK_DIR)/t1`, and prints logs/traces on failure.

## Dependencies and Integration Points
It is optionally used by nightly `ScenarioTests`, currently for file cache while block-cache scenario invocation is commented out due to known issues.

## Risks and Edge Cases
The local comparison directory is under `WORK_DIR` and may retain state if not cleaned. Known block-cache issues mean coverage is incomplete by design.

## Test Signals
Signals are successful Go scenario tests in normal and direct-IO modes plus failure log artifacts when scenario operations diverge.

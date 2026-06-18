# sources/distributed-fs/tahoe-lafs/integration/test_servers_of_happiness.py

## Purpose
Checks that an upload fails when a client's `shares.happy` requirement exceeds the number of available storage servers.

## Important APIs, Types, and Functions
Uses `util._create_node` to create a non-storage client `edna` with needed=3, happy=7, total=10, `util.await_client_ready` for readiness, and `_CollectOutputProtocol` to capture CLI output. `util.ProcessFailed` is the expected failure path.

## Control Flow
The test creates and starts Edna against the shared introducer and storage nodes, waits until it sees the grid, then spawns `allmydata.scripts.runner -d edna put __file__`. It expects the process deferred to fail, asserts `UploadUnhappinessError` appears in the captured output, and verifies the user-facing placement message mentions shares could be placed on only too few servers.

## State and Persistence
Creates a temp node directory named `edna` with Tahoe config reflecting the high happiness requirement. The attempted upload should not result in a successful immutable file capability.

## Dependencies and Integration Points
Depends on existing storage-node fixtures, introducer furl, flog gatherer, Tahoe CLI upload, and the upload happiness algorithm.

## Risks
The test assumes the fixture grid has fewer than seven usable storage servers. If future fixtures scale up, the failure assumption changes. It captures both stdout and stderr and relies on message substrings that may change with error formatting.

## Test Signals
The primary signal is a failed CLI upload containing `UploadUnhappinessError`; the secondary signal is human-readable placement diagnostics.

# sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_no_network.py

## Purpose
Smoke-tests the `NoNetworkGrid` harness used by many Tahoe tests, confirming it can start/stop and perform an immutable upload/download round trip.

## APIs / Types / Functions
- `Harness.setUp` starts a parent `MultiService` and `SameProcessStreamEndpointAssigner`.
- `Harness.grid` constructs a one-client, ten-server `NoNetworkGrid`.
- `test_create` starts and stops the grid.
- `test_upload` uploads `Data` and downloads through a URI-created node.

## Control Flow
The create test constructs and starts a grid, then stops it. The upload test attaches the grid to the service parent, uploads repeated byte data from client zero, creates a filenode from the returned URI, downloads bytes, and asserts equality.

## State And Persistence
Creates temporary grid service state, storage directories, clients, servers, and endpoint assignment state.

## Dependencies / Integration Points
Integrates `NoNetworkGrid`, immutable upload `Data`, `download_to_data`, Twisted services, and same-process endpoint assignment.

## Risks And Test Signals
Coverage is intentionally shallow and does not test failure simulation or mutable files. Passing tests signal the harness baseline is healthy for the broader no-network test suite.

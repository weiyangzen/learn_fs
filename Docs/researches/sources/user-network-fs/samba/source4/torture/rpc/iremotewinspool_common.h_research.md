# sources/user-network-fs/samba/source4/torture/rpc/iremotewinspool_common.h

## Purpose
This header declares shared data structures and helper APIs used by the iremotewinspool RPC tests and driver-install tests. It centralizes print-driver state, suite fixture context, client OS version identifiers, and helper prototypes.

## Important APIs, Types, And Functions
`REG_DRIVER_CONTROL_KEY` names the registry subtree used to validate installed printer drivers. `struct test_driver_info` tracks SMB connection state, parsed `spoolss_AddDriverInfo8`, local driver path metadata, server/share names, upload GUID directory, uploaded INF path, driver name, architecture, and optional core-driver INF. `struct test_iremotewinspool_context` holds the required object UUID, iremotewinspool pipe, server handle, driver info, and discovered environment. The header declares open/close printer helpers, environment lookup, printer-data reads, Winreg string initialization, client-info construction, and INF parsing.

## Control Flow
The header has no executable flow, but it defines the fixture contract: setup code fills `test_iremotewinspool_context`, optional driver setup attaches `test_driver_info`, tests reuse the open server handle and environment, and teardown consumes the same fields for cleanup.

## State And Persistence Behavior
The structures model both transient RPC handle state and persistent server artifacts created by driver tests, including files copied to `print$`, uploaded driver packages, installed driver registry keys, and driver-store INF paths. The fields are talloc-owned by the test context in the implementation files.

## Dependencies And Integration Points
The header includes the torture RPC harness and relies on generated types from Winspool/Spoolss/Winreg headers included by implementation files. It is the integration boundary between the generic iremotewinspool protocol tests, the shared helpers, and the driver package tests.

## Risks And Edge Cases
Because `test_driver_info` stores cleanup-critical paths like `print_upload_guid_dir` and `uploaded_inf_path`, setup failures can leave teardown with partially populated state. Callers need to ensure fields are initialized before driver cleanup is attempted. The OS-version enum only supports the build values encoded in the common implementation.

## Test Signals
The header itself has no runtime assertions. Its quality signal is compile-time agreement among the three iremotewinspool source files and correct propagation of shared handles, environment strings, and driver metadata.

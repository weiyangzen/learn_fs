# sources/user-network-fs/samba/source4/torture/rpc/frsapi.c

## Purpose
This file implements the `rpc.frsapi` suite for File Replication Service API RPC calls. It checks polling interval get/set behavior, replicated-path classification, forced replication, and informational levels.

## Important APIs, Types, And Functions
`torture_rpc_frsapi()` registers tests on `ndr_table_frsapi`. Helpers wrap `dcerpc_frsapi_GetDsPollingIntervalW_r`, `SetDsPollingIntervalW_r`, and `IsPathReplicated_r`. Top-level tests call `dcerpc_frsapi_ForceReplication_r` and `dcerpc_frsapi_InfoW_r`.

## Control Flow
`test_DsPollingIntervalW()` reads the current intervals, writes them back unchanged, then writes a zeroed long/short interval with the original current interval and finally expects the original values to be returned. `test_IsPathReplicated()` verifies invalid NULL path handling and then probes the server name, `\\server\SYSVOL`, and `C:\windows\sysvol\domain` for replica-set types 0, domain, and DFS. `test_InfoW()` loops levels 0 through 9, sending a pre-sized `frsapi_Info` structure and printing non-zero bytes from the returned blob.

## State And Persistence Behavior
Polling interval tests call the setter and may alter server FRS polling configuration if the server accepts the writes. The intended invariant is that a later read returns the original values, but the sequence still exercises persistent configuration. Force replication can trigger replication activity for the configured DNS domain and partner server.

## Dependencies And Integration Points
The file depends on generated FRSAPI NDR stubs, Samba configuration for `lpcfg_dnsdomain()`, DCE/RPC server-name helpers, WERROR assertions, and the torture RPC harness.

## Risks And Edge Cases
The polling interval sequence assumes server semantics normalize or ignore zero long/short values. Force replication depends on domain membership and FRS availability. `InfoW()` treats the returned blob as printable text and writes directly to stdout, which is a weak structured validation. Servers without FRS or SYSVOL behavior may return implementation-specific errors.

## Test Signals
Signals are WERR success for get/set, exact invalid-service-parameter for NULL path, WERR success across path/type combinations, successful force replication, and success for all ten `InfoW` levels with printable diagnostic blob output.

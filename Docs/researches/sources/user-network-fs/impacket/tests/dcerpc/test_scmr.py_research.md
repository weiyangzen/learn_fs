# sources/user-network-fs/impacket/tests/dcerpc/test_scmr.py

## Purpose
This file validates Impacket's Service Control Manager Remote Protocol (`scmr`) implementation against a live Windows service controller. It tests service manager open/query/control calls, service creation/change/delete workflows, service configuration variants, failure-action encoding, enumeration APIs, lock handling, object security, display/key name lookup, and remote service start/stop behavior.

## Important APIs, Types, and Functions
`SCMRTests` binds `scmr.MSRPC_UUID_SCMR` and authenticates. `get_service_handle()` opens `ServicesActive` with service-manager and service permissions. `open_or_create_service()` opens `TESTSVC` or creates it with `hRCreateServiceW`. `changeServiceAndQuery()` wraps `hRChangeServiceConfigW` plus `hRQueryServiceConfigW` and verifies changed fields. `query_service_config2()` implements the standard insufficient-buffer retry pattern for `RQueryServiceConfig2W`; `query_failure_actions()` parses returned binary layout with `struct.unpack`. Tests use `SC_ACTION`, `SC_ACTIONS`, trigger structures, service status/config structures, and `NULL`.

## Control Flow
Tests connect to SCMR, obtain an SCM handle, then either query built-in services such as `PlugPlay`, `RemoteRegistry`, and `CryptSvc`, or create a temporary `TESTSVC`. Configuration tests build an `RChangeServiceConfig2W` request and mutate the discriminated union by setting both `dwInfoLevel` and `Union.tag`. Many calls intentionally first request a zero-sized buffer, capture `ERROR_MORE_DATA` or `ERROR_INSUFFICIENT_BUFFER`, then retry with `pcbBytesNeeded`. Transport subclasses run SMB named-pipe and TCP variants; TCP uses NTLM packet privacy.

## State and Persistence Behavior
The file creates, changes, starts, stops, and deletes real Windows services. `TESTSVC` is normally deleted and handles are closed after configuration tests, and the newer failure-action tests use `finally` for cleanup. Some older flows catch broad exceptions and perform manual deletion, while other service control calls may leave target services stopped or started depending on environmental behavior. `RControlServiceCall` attempts to stop `CryptSvc`, waits, and starts it again.

## Dependencies and Integration Points
Dependencies include `impacket.dcerpc.v5.scmr`, `impacket.crypto.encryptSecret` for service account password encryption on SMB, `impacket.uuid.string_to_bin` for service trigger GUIDs, `impacket.dcerpc.v5.ndr.NULL`, and the shared `DCERPCTests` transport/credential harness. It depends on live Windows SCM behavior and common service names.

## Risks
The main risk is target-state mutation: creating services, changing service config, service account details, failure actions, privileges, triggers, and stopping a real crypto service can affect the remote machine. The class-name check `self.__class__.__name__ == 'SMBTransport'` appears suspicious because concrete classes are `SCMRTestsSMBTransport` and `SCMRTestsTCPTransport`, so the encrypted-password branch may be unreachable. Several tests are skipped or commented because behavior is unresolved. Binary parsing in `query_failure_actions()` assumes exact SCMR layout offsets.

## Test Signals
The strongest signals are configuration round trips, failure-action array count synchronization, omitted action-list preservation, buffer-size retry correctness, service enum/status parsing into `SERVICE_STATUS_PROCESS`, expected service already running/not active/dependent-services errors, and successful handle close/delete cleanup. Skipped tests mark incomplete coverage for service groups, notifications, and control-service extended calls.

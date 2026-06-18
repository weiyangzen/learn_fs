# sources/user-network-fs/samba/source4/torture/rpc/svcctl.c

## Purpose

`svcctl.c` tests the Service Control Manager RPC interface against the default `Spooler` service. It covers manager and service handle lifecycle, service status/configuration queries, service security descriptor get/set, control paths, dependent-service enumeration, and a no-op configuration update.

## Important APIs, Types, and Functions

`TORTURE_DEFAULT_SERVICE` is `Spooler`. Common wrappers are `test_OpenSCManager()`, `test_OpenService()`, and `test_CloseServiceHandle()`. Query tests include `test_QueryServiceStatus()`, `test_QueryServiceStatusEx()`, `test_QueryServiceConfigW()`, `test_QueryServiceConfig2W()`, `test_QueryServiceConfigEx()`, `test_QueryServiceObjectSecurity()`, `test_EnumServicesStatus()`, and `test_EnumDependentServicesW()`. Mutating or control-shaped tests include `test_SetServiceObjectSecurity()`, `test_StartServiceW()`, `test_ControlService()`, `test_ControlServiceExW()`, and `test_ChangeServiceConfigW()`.

## Control Flow

Almost every test opens the SCM with maximum allowed access, opens `Spooler`, performs one operation, then closes service and manager handles. Buffer-sized APIs first call with zero or undersized buffers and retry on `WERR_INSUFFICIENT_BUFFER` or `WERR_MORE_DATA`. Security descriptor tests query DACL bytes and parse them with `ndr_pull_security_descriptor`; the setter writes back the same DACL. `ChangeServiceConfigW` queries the current config and then calls `ChangeServiceConfigW` with the existing type/start/error fields and NULL optional fields, checking that NULL means preserve current values.

## State and Persistence Behavior

The suite is mostly read-only, but it does call setter/control APIs. `SetServiceObjectSecurity` writes back the exact queried DACL. `ChangeServiceConfigW` performs a no-op configuration write. `StartServiceW` expects `WERR_SERVICE_ALREADY_RUNNING`, and `ControlService`/`ControlServiceExW` deliberately use invalid controls or parameters to avoid stopping the service. Remote service state can still be touched in audit logs and permissions must allow these calls.

## Dependencies and Integration Points

The file uses generated `ndr_svcctl` client stubs, generated security NDR parsing, common torture RPC helpers, and a target exposing the SCM named pipe endpoint with a `Spooler` service. It also depends on Windows/Samba SCM error-code compatibility.

## Risks and Edge Cases

The hard-coded `Spooler` service may be disabled, absent, or protected. Setter calls require sufficient rights and may fail under restricted credentials. The code allocates raw buffers for NDR-packed service arrays and manually pulls `ENUM_SERVICE_STATUSW`; buffer length and returned count must stay consistent. Tests encode expected quirks such as only `QueryServiceConfigEx` level 8 succeeding and `ControlServiceExW` returning `WERR_INVALID_PARAMETER`.

## Test Signals

Passing tests indicate SCM open/close correctness, query buffer retry behavior, DACL retrieval/parsing, no-op DACL/config writes, expected invalid-control errors, and service enumeration decoding. Failures usually point to endpoint availability, access rights, service policy, or IDL marshalling issues.

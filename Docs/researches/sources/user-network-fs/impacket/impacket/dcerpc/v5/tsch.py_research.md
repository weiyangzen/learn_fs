# sources/user-network-fs/impacket/impacket/dcerpc/v5/tsch.py

## Purpose

`tsch.py` implements Impacket's [MS-TSCH] Task Scheduler Service RPC interface. It defines the scheduler UUID, scheduler constants, NDR request/response classes for opnums 0 through 19, helper functions for common calls, and a few binary `Structure` classes for legacy `.job` data and trigger records.

The module is a client-side RPC schema and helper layer. It does not schedule work locally; it marshals Task Scheduler requests to a bound remote `ITaskSchedulerService` endpoint.

## Important APIs, types, and functions

- `MSRPC_UUID_TSCHS` identifies `86D35949-83C9-4044-B424-DB363231FD0C` version 1.0.
- `DCERPCSessionError` renders HRESULTs through `hresult_errors` and low-word system errors through `system_errors`.
- Constants cover task flags, logon types, task states, registration flags, security flags, enumeration flags, run flags, and trigger enums.
- NDR array/pointer types include `TASK_NAMES_ARRAY`, `WSTR_ARRAY`, `GUID_ARRAY`, `SYSTEMTIME_ARRAY`, and `TASK_USER_CRED_ARRAY`.
- Scheduler structures include `TASK_USER_CRED`, `TASK_XML_ERROR_INFO`, plus binary `FIXDLEN_DATA`, `TRIGGERS`, `WEEKLY`, `MONTHLYDATE`, `MONTHLYDOW`, and `JOB_SIGNATURE`.
- RPC calls cover highest-version query, task registration/retrieval, folder creation, security get/set, folder/task/instance enumeration, instance info, stop/run/delete/rename, scheduled runtimes, last run info, task info, missed run count, and enable/disable.
- `OPNUMS` maps opnums 0 to 19 to request and response classes.
- Helper functions `hSchRpc*` create requests, normalize strings, handle optional arrays, and call `dce.request()`.

## Control flow

Runtime flow is linear:

1. A caller binds a DCE/RPC connection to `MSRPC_UUID_TSCHS`.
2. A helper creates the relevant `SchRpc*` request.
3. The helper applies `checkNullString()` to most scheduler path/XML/SDDL strings.
4. For array parameters, helpers append wrapped values: `hSchRpcRegisterTask` appends credentials when present, and `hSchRpcRun` appends each argument as an `LPWSTR`.
5. `dce.request()` sends the request and returns the response object.

`checkNullString()` is central. It returns `NULL` unchanged and appends `\x00` to non-null strings lacking a terminator.

## State and persistence behavior

The module keeps no local persistent state. Remote persistent effects include:

- `hSchRpcRegisterTask` can create, update, disable, or validate scheduled tasks depending on flags.
- `hSchRpcCreateFolder`, `hSchRpcDelete`, and `hSchRpcRename` mutate scheduler folder/task namespace state.
- `hSchRpcSetSecurity` mutates SDDL security descriptors.
- `hSchRpcRun`, stop helpers, and enable helpers mutate runtime state.

Task XML, credentials, paths, and SDDL are transmitted to the remote scheduler service. Callers are responsible for protecting credential material and avoiding accidental persistent task creation.

## Dependencies and integration points

- Depends on `impacket.dcerpc.v5.ndr` and `impacket.dcerpc.v5.dtypes` for NDR schema.
- Uses `impacket.structure.Structure` for fixed binary legacy task/job records.
- Uses `hresult_errors` and `system_errors` for error display.
- Integrates with the rest of Impacket through DCE/RPC transport and binding code. Typical transport is SMB named pipe or RPC endpoint mapper resolution to Task Scheduler.
- Test guidance in the header points to Impacket SMB_RPC tests.

## Risks and implementation notes

- `SCHED_S_TASK_RUNNING` and `SCHED_S_TASK_NOT_SCHEDULED` are both assigned `0x00041301`; that looks suspicious because these scheduler success codes are normally distinct.
- XML and SDDL are caller-provided and only NUL-normalized; semantic validation is left to the remote service.
- `hSchRpcRegisterTask` sets `pCreds` to `NULL` when empty but otherwise appends directly into `request['pCreds']`; tests should verify pointer/array initialization works for non-empty credentials.
- Many helpers default to broad values such as `0xffffffff` for security information, counts, or enumeration size; callers should restrict where needed.
- The binary `.job` structures are independent from the RPC calls and need separate binary fixture coverage.

## Test signals

Useful tests should cover:

- `checkNullString()` behavior for `NULL`, already-terminated strings, and unterminated strings.
- Opnum map coverage for all nineteen calls.
- Register/retrieve/delete task round trips with minimal XML.
- Credential-array registration behavior.
- Folder/task enumeration pagination through `startIndex` and `cRequested`.
- `hSchRpcRun` argument array marshalling.
- Error formatting for HRESULTs, low-word Win32 errors, and unknown values.
- Binary layout parsing for `FIXDLEN_DATA`, trigger variants, and `JOB_SIGNATURE`.

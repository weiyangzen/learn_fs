# sources/user-network-fs/impacket/impacket/dcerpc/v5/scmr.py

## Purpose

`sources/user-network-fs/impacket/impacket/dcerpc/v5/scmr.py` implements Impacket's bindings for the Service Control Manager Remote Protocol, `[MS-SCMR]`. It defines service-control constants, NDR structures, request/response classes, an opnum dispatch map, and helper wrappers for opening the service control manager, opening services, creating/configuring/deleting services, starting/stopping/controlling services, querying status/configuration/security, enumerating services, and working with newer service configuration structures. The source was read as a complete 1428-line file for this report.

## Important APIs, Types, and Functions

The file defines access constants for services and the SCM database, service type/start/error-control values, service control codes, service states, accepted controls, security information bits, `SERVICE_CONFIG_*` levels, failure-action values, SID type values, status and notify masks, trigger constants, trigger subtypes, and trigger data types. One notable constant spelling issue is `ERVICE_ACCEPT_TRIGGEREVENT`, missing the leading `S`.

Core handle and status types include `SC_RPC_HANDLE`, `SC_NOTIFY_RPC_HANDLE`, `SERVICE_STATUS`, `SERVICE_STATUS_PROCESS`, `QUERY_SERVICE_CONFIGW`, `SC_RPC_LOCK`, `ENUM_SERVICE_STATUSW`, and `QUERY_SERVICE_LOCK_STATUSW`. Configuration structures include `SERVICE_DESCRIPTIONW`, `SERVICE_FAILURE_ACTIONSW`, `SC_ACTION`, `SERVICE_FAILURE_ACTIONS_FLAG`, `SERVICE_DELAYED_AUTO_START_INFO`, `SERVICE_SID_INFO`, `SERVICE_RPC_REQUIRED_PRIVILEGES_INFO`, `SERVICE_PRESHUTDOWN_INFO`, trigger-related structures, preferred-node/runlevel/managed-account structures, and the tagged `SC_RPC_CONFIG_INFOW_UNION` wrapped by `SC_RPC_CONFIG_INFOW`.

Several structures synchronize length or count fields at marshal time. `SERVICE_FAILURE_ACTIONSW.getData()` updates `cActions` from `lpsaActions`; `SERVICE_RPC_REQUIRED_PRIVILEGES_INFO.getData()` updates `cbRequiredPrivileges`; `SERVICE_TRIGGER_SPECIFIC_DATA_ITEM.getData()` updates `cbData`; `SERVICE_TRIGGER.getData()` updates `cDataItems`; and `SERVICE_TRIGGER_INFO.getData()` updates `cTriggers`. `STRING_PTRSW` customizes a conformant array to hold `LPWSTR` elements for `RStartServiceW` arguments.

RPC call classes model implemented opnums including close, control, delete, lock/unlock database, query/set service security, query/set service status, boot config notification, change/create service, enumerate dependent/all/grouped services, open SCM/service, query config and lock status, start service, get display/key names, change/query config2, query status ex, enumerate status ex, WOW64 create service, notification-related calls, extended control, and query config ex. The file comments mark some newer notification/control paths as not working or returning bad stub data. `OPNUMS` maps these classes for dispatch.

Helper APIs include `hROpenSCManagerW()`, `hROpenServiceW()`, `hRCreateServiceW()`, `hRChangeServiceConfigW()`, `hRDeleteService()`, `hRStartServiceW()`, `hRControlService()`, `hRQueryServiceStatus()`, `hRQueryServiceConfigW()`, `hRQueryServiceObjectSecurity()`, `hRSetServiceObjectSecurity()`, `hREnumServicesStatusW()`, `hRLockServiceDatabase()`, `hRUnlockServiceDatabase()`, `hRGetServiceDisplayNameW()`, `hRGetServiceKeyNameW()`, `hREnumDependentServicesW()`, `hREnumServiceGroupW()`, and close/status helpers.

## Control Flow

Typical usage is: bind to `MSRPC_UUID_SCMR`, call `hROpenSCManagerW()` to get an SCM handle, open or create a service, query/change/start/control/delete it, then close handles with `hRCloseServiceHandle()`. Most helpers populate request fields, call `checkNullString()` for string fields where applicable, and dispatch via `dce.request()`.

The important local control flow is in query/enumeration helpers. `hRQueryServiceObjectSecurity()` starts with the supplied buffer size, catches `ERROR_INSUFFICIENT_BUFFER`, reads `pcbBytesNeeded` from the exception packet, and retries. `hRQueryServiceConfigW()` does the same for service config queries. `hREnumServicesStatusW()` sends a zero-sized enumeration request, catches `ERROR_MORE_DATA`, retries with `pcbBytesNeeded`, then parses the returned byte buffer with a local `ENUM_SERVICE_STATUSW2` structure. Because the returned buffer contains pointer-like offsets into the same blob, the helper reparses `lpDisplayName` and `lpServiceName` manually by subtracting four from the referent IDs and decoding `WIDESTR` data at those offsets. `hRStartServiceW()` sets `argv` to `NULL` when `argc` is zero or appends null-terminated `LPWSTR` entries for each argument when nonzero.

## State and Persistence Behavior

The module has no durable local state, but many helpers mutate persistent service configuration on the remote host. `hRCreateServiceW()`, `hRChangeServiceConfigW()`, config2 calls, `hRDeleteService()`, security descriptor setters, and start/control operations can alter installed services, credentials, startup behavior, security descriptors, runtime status, and boot behavior. Handles and locks are remote context state. Local state is limited to transient request objects, parsed enumeration records, and buffer sizes used for retry.

## Dependencies and Integration Points

`scmr.py` depends on `system_errors`, DCE/RPC data types (`DWORD`, `LPWSTR`, `LPBYTE`, `GUID`, `WIDESTR`, and others), NDR base classes and pointer/null-pointer helpers, `DCERPCException`, and `uuidtup_to_bin`. It integrates with Impacket's DCE/RPC runtime through `MSRPC_UUID_SCMR`, `OPNUMS`, and `dce.request()`. It is commonly consumed by Impacket tools and examples that create temporary services for remote execution, inspect service state, or modify service configuration over SMB named pipes.

## Risks and Edge Cases

SCMR is operationally sensitive: service creation, binary path changes, security descriptor changes, deletion, and start/stop controls can disrupt or compromise a target system. Defaults are broad; `hROpenServiceW()` defaults to `SERVICE_ALL_ACCESS`, and `hROpenSCManagerW()` asks for several service-management rights. `checkNullString()` has the same empty-string indexing hazard as related modules. `hRCreateServiceW()` and `hRChangeServiceConfigW()` require callers to provide dependency and password buffers with correct byte sizes; the helper notes that dependency strings must be null-terminated but does not construct multi-string buffers. Enumeration parsing depends on pointer/offset assumptions in the returned LPBYTE blob and can break if layout differs. The in-file comments explicitly warn that notification calls and `RControlServiceExW` are not working, so their presence in `OPNUMS` should not be mistaken for reliable helper support. The misspelled trigger-event constant can cause caller confusion.

## Test Signals

Useful tests include request-field tests for open/create/change/start helpers; null-termination tests for service names, database names, display names, and arguments; mocked DCE/RPC tests for insufficient-buffer and more-data retry paths; parser tests for `hREnumServicesStatusW()` using representative returned buffers; `getData()` synchronization tests for failure actions, required privileges, and trigger structures; smoke tests for query config/status/security against a controlled Windows target; and explicit negative tests documenting not-working notification/control-ex opnums so future fixes are intentional.

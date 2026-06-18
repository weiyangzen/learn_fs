# sources/user-network-fs/impacket/impacket/dcerpc/v5/tsts.py

## Purpose

`tsts.py` implements a large portion of the [MS-TSTS] Terminal Services Terminal Server Runtime Interface Protocol for Impacket. It defines UUIDs for several Terminal Services RPC interfaces, NDR helpers for Terminal Services strings, handles, enums, session/client/config/process structures, many RPC call classes, standalone helper functions, and endpoint wrapper classes that bind to the proper named pipe and expose those helpers as methods.

The file is intentionally mixed-maturity. Header comments define tags such as `#NOT_IMPLEMENTED`, `#DOES_NOT_WORK`, and `#OLD`, and the body contains many partially implemented or deprecated calls alongside working helpers.

## Important APIs, types, and functions

- Interface UUIDs include `TermSrvSession_UUID`, `TermSrvNotification_UUID`, `TermSrvEnumeration_UUID`, `RCMPublic_UUID`, `RcmListener_UUID`, `SessEnvPublicRpc_UUID`, and `LegacyAPI_UUID`.
- `DCERPCSessionError` displays TSTS errors using the low 16 bits against `system_errors`.
- Scalar/string helpers include custom `NDRENUM.dump`, `TS_WCHAR`, `TS_LPWCHAR`, `TS_CHAR`, `SYSTEM_TIMESTAMP`, stripped string subclasses, `ZEROPAD`, `getUnixTime`, `enum2value`, `binary_sid_to_string`, and `SID`.
- Handle abstractions include `context_handle`, `handle_t`, `ENUM_HANDLE`, `HLISTENER`, `SERVER_HANDLE`, `NOTIFY_HANDLE`, and `SESSION_HANDLE`.
- Enums cover message-box results, shutdown flags, hotkey modifiers, event flags, address families, information/state/security/shadow classes, reconnect/session/shadow request types, notification IDs, callback class, session flags, and result statuses.
- Data models cover session enumeration levels, execution environment data, listener enumeration, `LSMSESSIONINFORMATION`, `WINSTATIONCLIENT`, counters, extended session info, notification changes, user config, WinStation config, remote address union, all-process information, and SID conversion helpers.
- RPC call classes span TermSrvSession, TermSrvNotification, TermSrvEnumeration, RCMPublic, RCMListener, SessEnv public shadowing, and Legacy WinStation APIs.
- Helper functions prefixed `hRpc*` build requests and often normalize strings or interpret unusual success behavior.
- Endpoint wrapper classes `TermSrvSession`, `TermSrvNotification`, `TermSrvEnumeration`, `RCMPublic`, `RcmListener`, `SessEnvPublicRpc`, and `LegacyAPI` inherit `TSTSEndpoint`, bind to a named pipe/interface UUID, set packet privacy, and expose matching helper functions as bound methods.

## Control flow

There are two main calling styles:

1. Low-level style: caller binds a DCE/RPC connection manually and calls helper functions with `dce` plus request parameters.
2. Endpoint style: caller passes an existing SMB connection, target IP, and Kerberos flag to an endpoint wrapper. `TSTSEndpoint` builds an `ncacn_np` string binding, reuses the SMB connection, creates a DCE/RPC object, sets GSS negotiate when Kerberos is requested, sets packet privacy, connects, binds to the endpoint UUID, and aliases `self.request` to `self._dce.request`.

Helper control flow is mostly request-fill-send-return. A few helpers add special handling:

- `hRpcConnect` treats `DCERPCSessionError` code `0x1` as success.
- `hRpcLogoff` treats `0x10000000` as success.
- Legacy API helpers use `dce.request(..., checkError=False)` because those responses encode success as a trailing one-byte boolean rather than normal `rpcrt` error status.
- `hRpcWinStationGetProcessSid` retries with a larger SID buffer when the first call reports `ERROR_STATUS_BUFFER_TOO_SMALL`.
- Some RCMPublic helpers catch all exceptions and return `None`, trading detailed failure signals for best-effort querying.

## State and persistence behavior

Local state is kept in endpoint wrapper instances:

- The SMB connection, target IP, string binding, endpoint UUID, transport, and DCE/RPC object are stored for the endpoint lifetime.
- Context handles returned by open/register calls represent server-side state and must be closed/unregistered with the corresponding helper.
- `TSTSEndpoint` is a context manager; `__exit__` disconnects the DCE/RPC connection.

Remote effects can be significant:

- Session helpers can connect, disconnect, log off, display message boxes, query state, and inspect users/times/counters.
- Notification helpers can wait for state changes and register async notifications.
- Listener helpers can start/stop Terminal Services listeners.
- Legacy helpers can disconnect/reset sessions, shut down/reboot/log off systems via `RpcWinStationShutdownSystem`, terminate processes, shadow sessions, and alter security/configuration where calls work.
- Process helpers can enumerate processes and resolve SIDs.

## Dependencies and integration points

- Uses `impacket.dcerpc.v5.transport` to build named-pipe transports.
- Depends on many NDR/dtype primitives from `impacket.dcerpc.v5.ndr` and `impacket.dcerpc.v5.dtypes`.
- Uses `impacket.uuid` conversions for endpoint UUIDs and context handles.
- Uses `impacket.dcerpc.v5.rpcrt` authentication constants, especially `RPC_C_AUTHN_GSS_NEGOTIATE` and `RPC_C_AUTHN_LEVEL_PKT_PRIVACY`.
- Uses `impacket.dcerpc.v5.enum.Enum` and `impacket.system_errors`.
- Expected named pipes are `\pipe\LSM_API_service`, `\pipe\TermSrv_API_service`, `\pipe\SessEnvPublicRpc`, and `\pipe\Ctx_WinStation_API_service`.

## Risks and implementation notes

- The file contains explicit incomplete and non-working sections. `EXECENVDATAEX_LEVEL1`, `PROTOCOLCOUNTERS`, `CACHE_STATISTICS`, `PROTOCOLSTATUS`, `WINSTATIONCONFIG2`, and `CLIENT_STACK_ADDRESS` are pass-through placeholders; multiple RPC classes use `UNKNOWNDATA` or commented protocol signatures.
- Several helper implementations appear to instantiate the wrong request class: `hRpcWinStationCloseServerEx`, `hRpcWinStationIsHelpAssistantSession`, and `hRpcWinStationOpenSessionDirectory` create `RpcWinStationShadowStop()` instead of their matching request classes.
- `RpcConnectCallback` is commented as opnum 66 but sets `opnum = 61`, conflicting with `RpcWinStationIsHelpAssistantSession`.
- Broad `except:` blocks in `hRpcGetClientData` and `hRpcGetRemoteAddress` suppress all failure detail.
- Custom string/array classes and fixed-size padding functions rely on exact byte/character sizing; off-by-one errors can corrupt request marshalling.
- Legacy response handling bypasses normal RPC error checking and must inspect boolean/result fields carefully.
- Some helpers can perform disruptive administrative actions, including logoff, reset, process termination, and system shutdown.
- Endpoint wrappers always request packet privacy and require a valid SMB connection; callers need to manage authentication and SMB lifetime consistently.

## Test signals

Useful tests should cover:

- Unit tests for custom string decoding, stripped NUL behavior, `ZEROPAD`, timestamp conversion, enum rendering, SID conversion, and context handle tuple/null behavior.
- Binding tests for each endpoint wrapper, verifying named pipe, UUID, auth level, Kerberos auth type, and context-manager disconnect behavior.
- Session open/query/close and notification register/wait/unregister against a test Windows host.
- Enumeration helpers at levels 1, 2, and 3, including union tags and returned array parsing.
- RCMPublic client/config/last-input/remote-address/listener parsing, especially IPv4/IPv6 remote address unions.
- Legacy API tests with `checkError=False`, including open/close server, message, name/logon lookup, disconnect/reset, process enumeration, SID retry behavior, and error boolean interpretation.
- Regression tests for the wrong-request-class helpers and the `RpcConnectCallback` opnum mismatch.

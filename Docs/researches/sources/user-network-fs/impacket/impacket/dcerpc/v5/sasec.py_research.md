# sources/user-network-fs/impacket/impacket/dcerpc/v5/sasec.py

## Purpose

`sources/user-network-fs/impacket/impacket/dcerpc/v5/sasec.py` implements the Security Account Manager-style security account interface used by the Task Scheduler protocol family, identified in the file as `[MS-TSCH] SASec`. It defines the SASec interface UUID, a small set of NDR call classes, and helper wrappers for setting and retrieving task scheduler account credentials for named jobs and network-service account information. The source was read as a complete 180-line file for this report.

## Important APIs, Types, and Functions

The main constants are `MSRPC_UUID_SASEC`, `SASEC_HANDLE`, `PSASEC_HANDLE`, `MAX_BUFFER_SIZE = 273`, and `TASK_FLAG_RUN_ONLY_IF_LOGGED_ON`. `WORD_ARRAY` is the conformant array used as a UTF-16 code-unit buffer for account query responses.

The RPC classes are compact: `SASetAccountInformation` opnum 0 sets account, password, and flags for a job name; `SASetNSAccountInformation` opnum 1 sets account/password information without a specific job; `SAGetNSAccountInformation` opnum 2 queries network-service account information into a caller-sized word buffer; and `SAGetAccountInformation` opnum 3 queries account information for a specific job. Each response carries an `ErrorCode`. `OPNUMS` maps opnums 0 through 3 to these request/response pairs.

Helpers are `checkNullString()`, `hSASetAccountInformation()`, `hSASetNSAccountInformation()`, `hSAGetNSAccountInformation()`, and `hSAGetAccountInformation()`. The set helpers null-terminate job/account/password strings and dispatch the request. The get helpers allocate `ccBufferSize` zero words in `wszBuffer` before dispatching, using `MAX_BUFFER_SIZE` unless the caller overrides it.

## Control Flow

The flow is direct: callers bind to `MSRPC_UUID_SASEC`, supply a scheduler handle string, and call one of the four helpers. There is no adaptive retry or response parsing beyond NDR unmarshalling. Query helpers pre-size the output buffer by appending zero words in a Python loop, then rely on the server to fill the returned `WORD_ARRAY`.

## State and Persistence Behavior

The module has no local persistent state. Set operations can persistently alter task scheduler credential configuration on the remote host, including stored account names/passwords or run-only-if-logged-on behavior depending on flags. Get operations only allocate transient buffers and return remote account information in the response. The caller owns any remote handle lifecycle outside this file.

## Dependencies and Integration Points

`sasec.py` depends on Impacket NDR call/conformant-array classes, DCE/RPC scalar/string types (`DWORD`, `LPWSTR`, `ULONG`, `WSTR`, `NULL`), HRESULT error mappings, `uuidtup_to_bin`, and `DCERPCException`. It integrates with Impacket's DCE/RPC dispatcher through `MSRPC_UUID_SASEC`, `OPNUMS`, and `dce.request()`. Its domain is adjacent to the broader Task Scheduler RPC modules; callers usually combine it with task scheduler binding and handle acquisition code elsewhere.

## Risks and Edge Cases

The interface deals directly with account passwords, so callers must avoid logging request contents and should understand remote credential-storage effects. `checkNullString()` indexes the last character for non-`NULL` inputs, so empty strings are not safe inputs unless a caller passes an already valid representation. Query helpers use a fixed default buffer size and do not retry on insufficient-buffer style errors. The returned `WORD_ARRAY` is not decoded into a Python string by the helper, so callers must decode UTF-16 data carefully and trim terminators. Because this module uses HRESULT mappings, error interpretation differs from modules that use Win32 or NTSTATUS tables.

## Test Signals

Appropriate tests include request-construction checks for null termination and flag propagation; query-buffer sizing tests for default and custom `ccBufferSize`; mocked error tests for HRESULT formatting in `DCERPCSessionError`; integration smoke tests against a controlled scheduler service for set/get account information; and negative tests for empty strings, `NULL` passwords, small buffers, and access-denied responses.

# sources/user-network-fs/samba/source4/torture/rpc/browser.c

## Purpose
`browser.c` tests the Browser RPC interface, specifically `BrowserrQueryOtherDomains`. It validates accepted level 100 calls and error handling for missing containers and unsupported levels.

## Important APIs, types, and functions
The suite entry point is `torture_rpc_browser()`, and the test function is `test_BrowserrQueryOtherDomains()`. It uses generated `dcerpc_BrowserrQueryOtherDomains_r()`, `struct BrowserrQueryOtherDomains`, `struct BrowserrSrvInfo`, `BrowserrSrvInfo100Ctr`, `BrowserrSrvInfo101Ctr`, `srvsvc_NetSrvInfo100`, `srvsvc_NetSrvInfo101`, and `ndr_table_browser`.

## Control flow
The test builds `\\server` from the RPC pipe server name, initializes a `BrowserrSrvInfo` union, and calls level 100 first with an empty container and then with a preallocated one-entry container. Both should succeed and report zero total entries. It then sets the level 100 pointer to NULL and expects `WERR_INVALID_PARAMETER`. For level 101 with and without a container, and levels 102 and 0, it expects successful RPC transport but `WERR_INVALID_LEVEL`.

## State and persistence behavior
The test is read-only. It only allocates request/response containers and observes the browser service response. No browser database or domain state is changed.

## Dependencies and integration points
The file depends on generated Browser and SRVSVC-related NDR types, DCE/RPC torture interface registration, and browser service behavior on the target. It validates both NDR union arm handling and server-side level validation.

## Risks and edge cases
The test assumes no "other domains" are returned and asserts total entries zero. That is suitable for Samba's expected behavior but may be environment-sensitive if a server exposes browser domain entries. It also assumes invalid levels are reported as WERRORs with OK transport status.

## Test signals
Passing signals are OK transport for every call, WERR_OK and zero entries for valid level 100 calls, `WERR_INVALID_PARAMETER` for a NULL level 100 container, and `WERR_INVALID_LEVEL` for levels 101, 102, and 0.

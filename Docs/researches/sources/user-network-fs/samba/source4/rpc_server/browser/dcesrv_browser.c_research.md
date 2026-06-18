# sources/user-network-fs/samba/source4/rpc_server/browser/dcesrv_browser.c

Purpose: `dcesrv_browser.c` provides a mostly stubbed DCERPC endpoint server for the legacy Browser service pipe.

Important APIs, types, and functions: It implements handlers for Browser RPC operations including `BrowserrServerEnum`, `BrowserrDebugCall`, `BrowserrQueryOtherDomains`, reset/debug/statistics calls, `BrowserrSetNetlogonState`, `BrowserrQueryEmulatedDomains`, and `BrowserrServerEnumEx`.

Control flow: Nearly all operations immediately raise `DCERPC_FAULT_OP_RNG_ERROR`, indicating unsupported operation range. `BrowserrQueryOtherDomains` is partially implemented for info level 100: it validates the input union, allocates an empty `BrowserrSrvInfo100Ctr`, assigns zero entries, sets total entries to zero, and returns `WERR_OK`. Other levels return `WERR_INVALID_LEVEL`.

State and persistence behavior: No server state is stored or mutated. The one implemented path returns an allocated empty result under the call memory context.

Dependencies and integration points: It depends on DCERPC server declarations and generated browser NDR stubs (`ndr_browser_s.c`). It is part of Samba's RPC endpoint set for compatibility with clients that probe the browser pipe.

Risks: Clients expecting real Browser service enumeration/statistics will receive faults or empty domain data. The stub must still marshal level-100 output correctly to avoid client crashes.

Test signals: RPC tests should assert unsupported methods fault consistently, `BrowserrQueryOtherDomains` level 100 returns an empty success response, invalid levels fail, and NULL info100 input returns `WERR_INVALID_PARAMETER`.

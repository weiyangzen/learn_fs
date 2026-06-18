# sources/distributed-fs/xrootd/src/XrdSec/XrdSecPManager.cc

Purpose: Implements protocol discovery, loading, caching, and client/server protocol object creation for XRootD security protocols.

Important APIs and functions: `Find` returns a protocol bitmask and optional initializer arguments. `Get(host, endpoint, pname, err)` creates a server-side protocol. `Get(host, endpoint, XrdSecParameters&, err)` scans a server token for client-side candidates. Private `Add`, `Lookup`, and `ldPO` manage loaded protocol list entries and dynamic library resolution.

Control flow: Server configuration calls `Load`, which invokes `ldPO` to resolve `XrdSecProtocol<p>Object` and `XrdSecProtocol<p>Init`, run one-time initialization, and append the protocol. Client selection scans `&P=<name>[,<args>]` entries, honors `xrd.wantprot` or `XrdSecPROTOCOL`, lazily loads matching protocols, and advances `secparm.buffer/size` past failed candidates so callers can retry later.

State and persistence: `XrdSecProtList` entries are intentionally never freed and hold protocol id, arguments, bitmask, TLS-required flag, and factory pointer. `tlsProt` accumulates protocol names requiring TLS. `protnum` assigns shifting bitmasks until overflow. State is process-local.

Dependencies and integration points: Uses `XrdOucPinLoader`, `XrdOucErrInfo`, `XrdOucEnv`, `XrdVersionPlugin`, `XrdNetAddrInfo`, the builtin `host` protocol, and `XrdSecInterface` plug-in symbols.

Risks: Dynamic libraries are pinned by retaining function pointers after deleting the loader object. The constructor stores `protargs` as a string literal when no args are supplied, while the destructor never frees entries. `secparm.buffer` is mutated during scan, surprising callers that reuse it. Protocol-id and token parsing are bounded but still legacy C-string heavy. The debug export branch appears contradictory (`if (DebugON && ... && !DebugON)`).

Test signals: Load builtin `host`, load a valid shared protocol, fail missing `Init`/`Object`, parse multiple `&P=` candidates, filter with `XrdSecPROTOCOL`, verify `secparm` advancement, detect TLS prefixes, and enforce protocol bitmask overflow behavior.

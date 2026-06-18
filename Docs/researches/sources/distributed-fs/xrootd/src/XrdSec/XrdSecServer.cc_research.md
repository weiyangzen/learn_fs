# sources/distributed-fs/xrootd/src/XrdSec/XrdSecServer.cc

Purpose: Implements the default server-side `XrdSecService`: parses `sec.*` configuration, loads protocols and entity post-processors, builds security tokens, enforces protocol bindings, and initializes request protection.

Important APIs and functions: `XrdSecgetService` constructs/configures the service. `Configure` runs authentication then protection initialization. `getParms`, `getProtocol`, and `PostProcess` implement the public service contract. Directive handlers include `xenlib`, `xlevel`, `xpbind`, `xprot`, `xpparm`, and `xtrace`. Helpers `XrdSecProtBind`, `XrdSecProtParm`, `add2token`, and `ProtBind_Complete` manage host bindings and accumulated protocol arguments.

Control flow: Startup opens the config file, scans only `sec.` directives, loads configured protocols, accumulates default `&P=` token entries, resolves `protbind` host templates, optionally loads `SecEntityPin`, exports `XRDSECPROTOCOLS`, then configures local/remote protection. At login, `getParms` picks a host-specific or default token. `getProtocol` defaults null credentials to `host`, validates bindings when `only` enforcement is enabled, and delegates to `PManager`.

State and persistence: The service stores binding lists, default token buffers, config path, trace object, entity plugin handle, and flags. Static `PManager` caches loaded protocols across the process. No files are written, but environment variables are exported.

Dependencies and integration points: Uses `XrdOucStream`, `XrdOucPinKing`, `XrdSecEntityPin`, `XrdSecProtector`, `XrdNetAddr`, `XrdSysError`, `XrdOucTrace`, and the protocol manager. It is the implementation loaded by `XrdSecLoadSecService`.

Risks: Heavy use of raw allocation and linked lists makes startup error paths leak-tolerant but hard to unwind. `host` authentication can negate other default protocols. `protbind only` enforcement depends on protocol bitmasks and host template matching. `XrdSecProtParm` buffers are fixed at 4096 bytes. Constructor allocates `STBuff` without checking. `getParms` uses hostname matching and may return no auth for `none` bindings.

Test signals: Config files with no protocols, duplicate protocols, invalid protocol ids, missing libraries, `protparm` before/after protocol, wildcard and exact `protbind`, `only` enforcement, `entitylib ++`, trace toggles, protection levels/options, local/remote split, and `PostProcess` accept/reject.

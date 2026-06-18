## sources/distributed-fs/xrootd/src/Xrd/XrdProtLoad.cc

Purpose: loads built-in or shared-library protocol implementations, maps protocols to ports, selects the matching protocol for a new link, handles optional TLS-first matching, and aggregates protocol statistics.

Important APIs/types/functions: static `Load()` obtains a protocol object and registers it. `Port()` overloads query or record protocol-port mappings. Constructor builds `myProt` for one listening port, inserting `-1` as a TLS negotiation marker before TLS protocols. `Process()` negotiates TLS when requested, calls each protocol's `Match()`, installs the matched protocol/name, activates the link, and processes the first request. `Statistics()` concatenates protocol stats. `getProtocol()` and `getProtocolPort()` resolve built-in or plugin entry points.

Control flow: configuration asks each protocol for its port, loads it, and maps it. Accept loops attach an `XrdProtLoad` instance to new links. The loader probes protocols in port order; on match it replaces itself with the real protocol and activates polling.

State/persistence: static arrays store up to eight protocol names/objects and plugin handles. `portVec` records port/protocol/TLS mappings. Loader instances keep a signed-char protocol sequence for their port.

Dependencies/integration: depends on `XrdOucPinLoader`, `XrdProtocol`, `XrdLink`, version checks, global logging, and TLS link upgrade support.

Risks: protocol index handling is one-based in `Load()`/`Port()` and zero-based in arrays; off-by-one regressions would misroute ports. `myProt` uses `signed char`, limiting sentinel/index values to the small `ProtoMax`. Failed TLS negotiation sets link error text and closes. Plugin symbol resolution must match `XrdgetProtocol` and optional `XrdgetProtocolPort`.

Test signals: load built-in and plugin protocols, duplicate/max protocol counts, port mapping for TLS and non-TLS on the same port, failed TLS negotiation, no-match close reason, first-request processing shortcut, and stats concatenation buffer accounting.
